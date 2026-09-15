from typing import TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class RyujinState(TypedDict):
    # Main conversation
    messages: Annotated[list[BaseMessage], add_messages]

    # Coding Agent internal Worker ↔ ToolNode history
    coding_history: Annotated[list[BaseMessage], add_messages]

    # Coding Planner output
    task_type: str
    plan: list[str]

    requires_execution: bool
    requires_testing: bool
    requires_web_search: bool

    # Final Coding Agent output
    coding_solution: str