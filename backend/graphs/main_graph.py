from typing import Literal

from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END

from backend.graphs.state import RyujinState
from backend.graphs.checkpointer import checkpointer

from backend.graphs.general_graph import general_graph
from backend.graphs.coding_graph import coding_graph

from dotenv import load_dotenv

load_dotenv()


llm = ChatOpenAI(model="gpt-5-mini")


class SupervisorDecision(BaseModel):
    next: Literal["general", "coding"]


supervisor_llm = llm.with_structured_output(SupervisorDecision)


def supervisor(state: RyujinState) -> RyujinState:

    messages = [
        SystemMessage(
            content="""
You are the Supervisor of Ryujin AI.

Your job is to decide which specialized agent should handle
the user's request.

Available agents:

GENERAL:
- General questions and reasoning
- Basic calculations
- Web search for general information
- Wikipedia-based factual information
- Unit conversion
- Current date and time

CODING:
- Generate code
- Debug code
- Explain code
- Execute or test code
- Review and improve coding solutions

Routing rules:

Choose "coding" when the user's request involves writing,
debugging, explaining, testing, or working with code.

Choose "general" for general questions, reasoning,
calculations, or other requests that do not primarily
require the Coding Agent.

Return only the routing decision.
Do not answer the user's question.
"""
        ),
        *state["messages"],
    ]

    decision = supervisor_llm.invoke(messages)

    return {
        "next": decision.next,
    }

def supervisor_router(state: RyujinState) -> Literal["general", "coding"]:

    return state["next"]

builder = StateGraph(RyujinState)

builder.add_node("supervisor", supervisor)
builder.add_node("general", general_graph)
builder.add_node("coding", coding_graph)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges(
    "supervisor",
    supervisor_router,
    {
        "general": "general",
        "coding": "coding"
    }
)
builder.add_edge("general", END)
builder.add_edge("coding", END)


main_graph = builder.compile(checkpointer=checkpointer)