from langchain_core.messages import HumanMessage

from backend.graphs.coding_graph import coding_graph

result = coding_graph.invoke(
    {
        "messages": [
            HumanMessage(
                content="Write a Python function to calculate factorial."
            )
        ],
        "coding_history": [],
        "review_iterations": 0,
    }
)
print(result)