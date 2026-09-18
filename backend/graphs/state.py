from typing import TypedDict, Annotated ,Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class RyujinState(TypedDict):
    # Main conversation
    messages: Annotated[list[BaseMessage], add_messages]

    files: list[dict]

    next : Literal["general", "coding", "research"]

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
    review_decision: Literal["approved", "not_approved"]
    review_issues: list[str]
    review_iterations: int
  
    research_history: Annotated[list[BaseMessage], add_messages]

    research_plan: list[str]

    requires_rag: bool
    requires_web_search: bool
    requires_wikipedia: bool

    research_findings: str

    research_decision: Literal["approved", "not_approved"]
    research_issues: list[str]
    research_iterations: int

    