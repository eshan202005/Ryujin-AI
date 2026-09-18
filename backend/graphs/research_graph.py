from typing import Literal 

from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langgraph.config import get_stream_writer
from langchain_core.messages import AIMessage

from backend.graphs.state import RyujinState
from backend.agents.research.tools import (
    rag_search,
    search_tool,
    wikipedia_tool,
)

MAX_RESEARCH_ITERATIONS = 3

llm = ChatOpenAI(model="gpt-5-mini")

tools = [rag_search, search_tool, wikipedia_tool]

tool_node = ToolNode(
    tools,
    messages_key="research_history",
)
researcher_llm = llm.bind_tools(tools)


class ResearchPlan(BaseModel):
    steps: list[str]
    requires_rag: bool
    requires_web_search: bool
    requires_wikipedia: bool

class ResearchReview(BaseModel):
    decision: Literal["approved", "not_approved"]
    issues: list[str]


planner_llm = llm.with_structured_output(ResearchPlan)
reviewer_llm = ChatOpenAI(model="gpt-5.4-nano").with_structured_output(ResearchReview)
optimizer_llm = ChatOpenAI(model="gpt-5-mini")
finalizer_llm = ChatOpenAI(model="gpt-5-mini")



def initialize_research_state(state: RyujinState) -> RyujinState:
    return {
        "research_history": [],
        "research_iterations": 0,
    }


def research_planner(state: RyujinState) -> RyujinState:

    messages = [
        SystemMessage(
            content="""
You are the Research Planner for Ryujin AI.

Your job is to create a research plan for the user's request.

Determine:
1. What research steps are required.
2. Whether the user's uploaded documents should be searched.
3. Whether web search is required.
4. Whether Wikipedia is useful.

Use RAG when information should come from the user's
uploaded documents.

Use web search when current, broad, or external information
is required.

Use Wikipedia when general factual/background information
would be useful.

Do not answer the user's question.
Only create the research plan.
"""
        ),
        *state["messages"],
    ]

    plan = planner_llm.invoke(messages)

    return {
        "research_plan": plan.steps,
        "requires_rag": plan.requires_rag,
        "requires_web_search": plan.requires_web_search,
        "requires_wikipedia": plan.requires_wikipedia,
    }

def researcher(state: RyujinState) -> RyujinState:

    messages = [
        SystemMessage(
            content="""
You are the Researcher for Ryujin AI.

Your job is to execute the research plan.

You have access to three research tools:

1. RAG
   Search the user's uploaded documents.

2. Web Search
   Search the internet for external or current information.

3. Wikipedia
   Retrieve general factual and background information.

Use the tools when they are needed.

Follow the research plan carefully.

IMPORTANT:
- When you need information from a tool, make the tool call.
- A tool call is NOT the end of your research.
- After receiving tool results, continue researching if more
  information is needed.
- Do not provide research findings while making a tool call.
- Only provide research findings when you have gathered enough
  information and completed the research plan.
- Your final response should contain the complete research findings
  for the Reviewer.
- Do not produce the final user-facing answer.
"""
        ),

        *state["messages"],

        SystemMessage(
            content=f"""
Research Plan:
{state["research_plan"]}

Required research sources:
RAG: {state["requires_rag"]}
Web Search: {state["requires_web_search"]}
Wikipedia: {state["requires_wikipedia"]}
"""
        ),

        *state["research_history"],
    ]

    response = researcher_llm.invoke(messages)

    return {
        "research_history": [response],
        "research_findings": response.content,
    }

def research_tool_router(state: RyujinState,) -> Literal["tools", "reviewer"]:

    last_message = state["research_history"][-1]

    if last_message.tool_calls:
        return "tools"

    return "reviewer"


def research_reviewer(state: RyujinState) -> RyujinState:

    messages = [
        SystemMessage(
            content="""
You are the Research Reviewer for Ryujin AI.

Your job is to review the research produced by the Researcher.

Check:

1. Whether the research plan was completed.
2. Whether the findings sufficiently answer the user's request.
3. Whether the required sources were actually used when necessary.
4. Whether important information or research gaps remain.

If the research is sufficient:
- Return "approved".
- Return an empty issues list.

If the research is insufficient:
- Return "not_approved".
- Clearly describe what is missing.

Do not perform new research.
Do not write the final user-facing answer.
"""
        ),
        *state["messages"],
        SystemMessage(
            content=f"""
Research Plan:
{state["research_plan"]}

Required Sources:
RAG: {state["requires_rag"]}
Web Search: {state["requires_web_search"]}
Wikipedia: {state["requires_wikipedia"]}

Research Findings:
{state["research_findings"]}

Research History:
{state["research_history"]}
"""
        ),
    ]

    review = reviewer_llm.invoke(messages)

    return {
        "research_decision": review.decision,
        "research_issues": review.issues,
    }

def research_review_router(
    state: RyujinState,
) -> Literal["optimizer", "finalizer"]:

    if state["research_decision"] == "approved":
        return "finalizer"

    if state["research_iterations"] >= MAX_RESEARCH_ITERATIONS:
        return "finalizer"

    return "optimizer"

def research_optimizer(state: RyujinState) -> RyujinState:

    messages = [
        SystemMessage(
            content="""
You are the Research Optimizer for Ryujin AI.

Your job is to improve the existing research findings
based on the issues identified by the Research Reviewer.

Address the reviewer's issues using the existing research
information.

Return ONLY the improved research findings.

Do not create a new research plan.
Do not answer the user directly.
Do not mention the review process.
"""
        ),
        *state["messages"],
        SystemMessage(
            content=f"""
Current Research Findings:
{state["research_findings"]}

Reviewer Issues:
{state["research_issues"]}
"""
        ),
    ]

    response = optimizer_llm.invoke(messages)

    return {
        "research_findings": response.content,
        "research_iterations": state["research_iterations"] + 1,
    }

def research_finalizer(state: RyujinState) -> RyujinState:

    messages = [
        SystemMessage(
            content="""
You are the Finalizer for Ryujin AI's Research Agent.

Use the research findings to answer the user's original question.

Requirements:

- Give a clear and accurate answer.
- Use the gathered research.
- Do not mention internal agents, planning, reviewing,
  optimization, or tool execution.
- Do not invent information that was not supported by the research.
"""
        ),
        *state["messages"],
        SystemMessage(
            content=f"""
Research Findings:

{state["research_findings"]}
"""
        ),
    ]

    writer = get_stream_writer()

    full_response = ""

    for chunk in finalizer_llm.stream(messages):

        if chunk.content:

            full_response += chunk.content

            writer({
                "type": "research_final_response",
                "content": chunk.content,
            })

    return {
        "messages": [
            AIMessage(content=full_response)
        ]
    }





builder = StateGraph(RyujinState)

builder.add_node("initialize_research_state",initialize_research_state)
builder.add_node("research_planner",research_planner)
builder.add_node("researcher",researcher)
builder.add_node("tool_node",tool_node)
builder.add_node("research_reviewer",research_reviewer)
builder.add_node("research_optimizer",research_optimizer)
builder.add_node("research_finalizer",research_finalizer)

builder.add_edge(START,"initialize_research_state")

builder.add_edge("initialize_research_state","research_planner")
builder.add_edge("research_planner","researcher")

builder.add_conditional_edges(
    "researcher",
    research_tool_router,
    {
        "tools": "tool_node",
        "reviewer": "research_reviewer",
    },
)

builder.add_edge("tool_node","researcher")
builder.add_conditional_edges(
    "research_reviewer",
    research_review_router,
    {
        "optimizer": "research_optimizer",
        "finalizer": "research_finalizer",
    },
)

builder.add_edge(
    "research_optimizer",
    "research_reviewer",
)

builder.add_edge(
    "research_finalizer",
    END,
)

research_graph = builder.compile()