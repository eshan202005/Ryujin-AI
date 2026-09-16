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

    if result.get("final_response"):
        return result["final_response"]

    return result["messages"][-1].content


async def stream_chat(message: str, thread_id: str):

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    async for namespace, chunk in main_graph.astream(
        {
            "messages": [
                HumanMessage(content=message)
            ]
        },
        config=config,
        stream_mode="messages",
        subgraphs=True,
    ):

        message_chunk, metadata = chunk

        node = metadata.get("langgraph_node")

        if node not in ["chat_agent", "coding_finalizer"]:
            continue

        if message_chunk.content:
            yield message_chunk.content