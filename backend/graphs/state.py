from typing import TypedDict, Annotated, Literal
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class RyujinState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

    task_type: Literal[
        "generate",
        "debug",
        "explain",
    ]

    plan: list[str]
    requires_execution: bool
    requires_testing: bool
    requires_web_search: bool
    coding_result: str
    review_score : int
    review_feedback: str
    iteration: int
