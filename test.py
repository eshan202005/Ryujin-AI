from langchain_core.messages import HumanMessage

from backend.graphs.coding_graph import coding_graph


result = coding_graph.invoke(
    {
        "messages": [
            HumanMessage(
                content="Write a Python function to reverse a string."
            )
        ]
    }
)

print(result)