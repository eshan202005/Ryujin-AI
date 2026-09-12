from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun

@tool
def calculator_tool(a: float, b: float, operation: str) -> float:
    """Perform a basic calculation."""

    if operation == "add":
        return a + b

    elif operation == "subtract":
        return a - b

    elif operation == "multiply":
        return a * b

    elif operation == "divide":
        if b == 0:
            return 0
        return a / b

    else:
        return 0
search_tool = DuckDuckGoSearchRun()    