from langchain_core.messages import HumanMessage
from backend.graphs.chat_graph import chat_graph

async def chat(message: str) -> str:

    result = await chat_graph.ainvoke(
        {
            "messages": [
                HumanMessage(content=message)
            ]
        }
    )

    return result["messages"][-1].content