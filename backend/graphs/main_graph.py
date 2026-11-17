from typing import Literal

from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END

from backend.graphs.state import RyujinState
from backend.graphs.checkpointer import checkpointer

from backend.graphs.general_graph import general_graph
from backend.graphs.coding_graph import coding_graph
from backend.graphs.research_graph import research_graph
from backend.graphs.writing_graph import writing_graph

from dotenv import load_dotenv

load_dotenv()


llm = ChatOpenAI(model="gpt-5-mini")


class SupervisorDecision(BaseModel):
    next: Literal["general", "coding", "research", "writing"]


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

RESEARCH:
- Research questions requiring multiple sources
- Search the user's uploaded documents
- Current or external information requiring web search
- Factual/background research using Wikipedia

WRITING:
- Create new prose such as emails, posts, articles, stories, and job descriptions
- Revise or rewrite supplied text
- Proofread grammar, spelling, punctuation, and clarity

Routing rules:

Choose "coding" when the user's request involves programming code,
including generating, debugging, explaining, or testing code.

Choose "writing" when the main request is to create, revise,
rewrite, or proofread prose. Writing code belongs to "coding".

Choose "general" for general questions, reasoning,
calculations, or other requests that do not primarily
require the Coding Agent.

Choose "research" when the user's request requires
research, document retrieval, web research, or gathering
information from multiple sources.

When a request primarily needs research before content creation,
choose "research". Otherwise, choose "writing" for the writing task.

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

def supervisor_router(
    state: RyujinState,
) -> Literal["general", "coding", "research", "writing"]:

    return state["next"]

builder = StateGraph(RyujinState)

builder.add_node("supervisor", supervisor)
builder.add_node("general", general_graph)
builder.add_node("coding", coding_graph)
builder.add_node("research", research_graph)
builder.add_node("writing", writing_graph)

builder.add_edge(START, "supervisor")
builder.add_conditional_edges(
    "supervisor",
    supervisor_router,
    {
        "general": "general",
        "coding": "coding",
        "research": "research",
        "writing": "writing",
    }
)
builder.add_edge("general", END)
builder.add_edge("coding", END)
builder.add_edge("research", END)
builder.add_edge("writing", END)


main_graph = builder.compile(checkpointer=checkpointer)
