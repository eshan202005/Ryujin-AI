from langchain_core.messages import HumanMessage

from backend.graphs.chat_graph import chat_graph


async def chat(message: str, thread_id: str) -> str:

    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    result = await chat_graph.ainvoke(
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

    async for message_chunk, metadata in chat_graph.astream(
        {
            "messages": [
                HumanMessage(content=message)
            ]
        },
        config=config,
        stream_mode="messages",
    ):
        if message_chunk.content:
            yield message_chunk.content