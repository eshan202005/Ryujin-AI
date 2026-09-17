from langchain_core.messages import HumanMessage

from backend.graphs.main_graph import main_graph


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


async def stream_chat(message: str, thread_id: str):

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
        stream_mode=["messages", "custom"],
        subgraphs=True,
        version="v2",
    ):

        # -----------------------------
        # LLM message stream
        # -----------------------------
        if chunk["type"] == "messages":

            message_chunk, metadata = chunk["data"]

            node = metadata.get("langgraph_node")

            # Only General Agent
            if node != "chat_agent":
                continue

            if message_chunk.content:
                yield message_chunk.content

        # -----------------------------
        # Custom stream
        # -----------------------------
        elif chunk["type"] == "custom":

            data = chunk["data"]

            if not isinstance(data, dict):
                continue

            if data.get("type") != "coding_final_response":
                continue

            content = data.get("content")

            if content:
                yield content