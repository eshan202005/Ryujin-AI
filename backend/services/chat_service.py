import json
import logging

from langchain_core.messages import HumanMessage

from backend.graphs.main_graph import main_graph

logger = logging.getLogger(__name__)

_AGENTS = {name: f"{name.title()} Agent" for name in ("general", "coding", "research", "writing")}
_TOOLS = {
    "duckduckgo_search": "Web search",
    "wikipedia": "Wikipedia",
    "rag_search": "Document search",
    "python_execution": "Python execution",
    "run_tests": "Running tests",
    "calculator_tool": "Calculator",
    "unit_conversion": "Unit conversion",
    "current_datetime": "Date and time",
}


def _task_status(chunk):
    """Expose execution labels only, never tool arguments or internal messages."""
    task = chunk["data"]
    if "input" not in task:
        return None
    node = task["name"]
    if node == "supervisor":
        return "Choosing an agent..."
    agent = _AGENTS.get(node)
    for namespace in chunk.get("ns", ()):
        agent = _AGENTS.get(namespace.split(":", 1)[0], agent)
    if not agent:
        return None
    if node == "tool_node":
        state = task["input"]
        history_key = {"Coding Agent": "coding_history", "Research Agent": "research_history"}.get(agent, "messages")
        history = state.get(history_key, [])
        calls = getattr(history[-1], "tool_calls", []) if history else []
        names = list(dict.fromkeys(_TOOLS.get(call["name"], call["name"].replace("_", " ")) for call in calls))
        return f"{agent} · {', '.join(names) if names else 'Using tools'}"
    stages = {"planner": "Planning", "worker": "Working", "reviewer": "Reviewing", "optimizer": "Revising", "reviser": "Revising", "finalizer": "Writing response"}
    for suffix, label in stages.items():
        if node.endswith(suffix):
            return f"{agent} · {label}"
    return f"{agent} · Working"


def _event(kind, **data):
    return json.dumps({"type": kind, **data}, ensure_ascii=False) + "\n"


async def chat(message: str, thread_id: str) -> str:

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = await main_graph.ainvoke(
        {
            "messages": [
                HumanMessage(content=message)
            ]
        },
        config=config,
    )

    return result["messages"][-1].content


async def stream_chat(message: str, thread_id: str, include_status: bool = False):
    try:
        async for content in _stream_chat(message, thread_id, include_status):
            yield content
    except Exception:
        if not include_status:
            raise
        logger.exception("Chat stream failed")
        yield _event("error", message="Ryujin could not finish this response. Please try again.")


async def _stream_chat(message: str, thread_id: str, include_status: bool):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    async for chunk in main_graph.astream(
        {
            "messages": [
                HumanMessage(content=message)
            ]
        },
        config=config,
        stream_mode=["messages", "custom", "tasks"] if include_status else ["messages", "custom"],
        subgraphs=True,
        version="v2",
    ):

        # -----------------------------
        # LLM message stream
        # -----------------------------
        if chunk["type"] == "tasks":
            label = _task_status(chunk)
            if label:
                yield _event("status", label=label)

        elif chunk["type"] == "messages":

            message_chunk, metadata = chunk["data"]

            node = metadata.get("langgraph_node")

            # Only stream General Agent's direct LLM response
            if node == "chat_agent":

                if message_chunk.content:
                    yield _event("token", content=message_chunk.content) if include_status else message_chunk.content

        # -----------------------------
        # Custom stream
        # -----------------------------
        elif chunk["type"] == "custom":

            data = chunk["data"]

            if not isinstance(data, dict):
                continue

            event_type = data.get("type")

            # Specialized agent finalizer streams
            if event_type not in {
                "coding_final_response",
                "research_final_response",
                "writing_final_response",
            }:
                continue

            content = data.get("content")

            if content:
                yield _event("token", content=content) if include_status else content

    if include_status:
        yield _event("done")
