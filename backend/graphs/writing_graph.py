from typing import Literal

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.config import get_stream_writer
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel

from backend.graphs.state import RyujinState


load_dotenv()

MAX_WRITING_REVISIONS = 3

llm = ChatOpenAI(
    model="gpt-5-mini",
    reasoning_effort="low",
    timeout=90,
    max_retries=0,
)


class WritingPlan(BaseModel):
    task_type: Literal["create", "revise", "proofread"]
    steps: list[str]
    audience: str
    tone: str
    format: str


class WritingReview(BaseModel):
    decision: Literal["approved", "not_approved"]
    issues: list[str]


planner_llm = ChatOpenAI(
    model="gpt-5-mini",
    reasoning_effort="minimal",
    max_tokens=4096,
    timeout=45,
    max_retries=0,
).with_structured_output(WritingPlan, method="function_calling")
reviewer_llm = ChatOpenAI(
    model="gpt-5.4-nano", timeout=45, max_retries=0
).with_structured_output(
    WritingReview
)
finalizer_llm = ChatOpenAI(
    model="gpt-5-mini", reasoning_effort="minimal", timeout=60, max_retries=0
)


def initialize_writing_state(state: RyujinState) -> RyujinState:
    return {
        "writing_task_type": "create",
        "writing_plan": [],
        "writing_audience": "Not specified",
        "writing_tone": "Not specified",
        "writing_format": "Not specified",
        "writing_draft": "",
        "writing_decision": "not_approved",
        "writing_issues": [],
        "writing_iterations": 0,
    }


def writing_planner(state: RyujinState) -> RyujinState:
    messages = [
        SystemMessage(
            content="""
You are the planner for Ryujin AI's Writing Agent.

Analyze the user's writing request and create a short, practical plan.

Classify the request as exactly one of:
- create: produce new written content
- revise: rewrite, expand, shorten, or otherwise improve supplied content
- proofread: correct grammar, spelling, punctuation, and clarity while preserving meaning

Identify the intended audience, tone, and format from the request or supplied
content. If any are not specified and cannot be reasonably inferred, use
"Not specified". Create steps that capture the user's requirements, including
any requested length, structure, or constraints.

Keep the plan concise, with at most five short steps.
Do not write or revise the requested content. Only return the structured plan.
"""
        ),
        *state["messages"],
    ]

    plan = planner_llm.invoke(messages)

    return {
        "writing_task_type": plan.task_type,
        "writing_plan": plan.steps,
        "writing_audience": plan.audience,
        "writing_tone": plan.tone,
        "writing_format": plan.format,
    }


def writing_worker(state: RyujinState) -> RyujinState:
    messages = [
        SystemMessage(
            content=f"""
You are Ryujin AI's Writing Agent. Create the requested text using the user's
conversation and the planner's brief below.

Task type: {state['writing_task_type']}
Audience: {state['writing_audience']}
Tone: {state['writing_tone']}
Format: {state['writing_format']}

Plan:
{chr(10).join(f'- {step}' for step in state['writing_plan'])}

Instructions:
- Follow the requested content, length, structure, tone, and format.
- For revisions and proofreading, preserve the user's intended meaning.
- Do not invent factual details, quotes, or citations.
- Return the complete draft without describing your process.
"""
        ),
        *state["messages"],
    ]

    response = llm.invoke(messages)

    return {
        "writing_draft": response.content,
    }


def writing_reviewer(state: RyujinState) -> RyujinState:
    messages = [
        SystemMessage(
            content=f"""
You are the reviewer for Ryujin AI's Writing Agent. Evaluate the draft against
the user's original request and the planner's brief. Do not rewrite the draft.

Task type: {state['writing_task_type']}
Audience: {state['writing_audience']}
Tone: {state['writing_tone']}
Format: {state['writing_format']}

Plan:
{chr(10).join(f'- {step}' for step in state['writing_plan'])}

Draft:
{state['writing_draft']}

Check whether the draft fulfills the request, follows the requested audience,
tone, format, and constraints, and is clear and coherent. For revisions or
proofreading, check that the user's meaning is preserved. Identify unsupported
facts, quotes, or citations as issues.

Approve a complete draft with an empty issues list. Otherwise, reject it and
list specific, actionable changes needed. Return only the structured review.
"""
        ),
        *state["messages"],
    ]

    review = reviewer_llm.invoke(messages)

    return {
        "writing_decision": review.decision,
        "writing_issues": review.issues,
    }


def writing_reviser(state: RyujinState) -> RyujinState:
    messages = [
        SystemMessage(
            content=f"""
You are the Reviser for Ryujin AI's Writing Agent. Improve the current draft by
addressing the reviewer's issues while preserving the user's intent.

Task type: {state['writing_task_type']}
Audience: {state['writing_audience']}
Tone: {state['writing_tone']}
Format: {state['writing_format']}

Original plan:
{chr(10).join(f'- {step}' for step in state['writing_plan'])}

Current draft:
{state['writing_draft']}

Reviewer issues:
{chr(10).join(f'- {issue}' for issue in state['writing_issues'])}

Return the complete improved draft only. Do not add unsupported facts or
citations, and do not mention the review process.
"""
        ),
        *state["messages"],
    ]

    response = llm.invoke(messages)

    return {
        "writing_draft": response.content,
        "writing_iterations": state["writing_iterations"] + 1,
    }


def writing_finalizer(state: RyujinState) -> RyujinState:
    messages = [
        SystemMessage(
            content=f"""
Present the completed writing draft to the user as the final response.

Preserve its content, tone, and formatting. Do not mention the internal planning,
review, or revision process.

Completed draft:
{state['writing_draft']}
"""
        ),
    ]

    stream_writer = get_stream_writer()
    full_response = ""

    for chunk in finalizer_llm.stream(messages):
        if chunk.content:
            full_response += chunk.content
            stream_writer(
                {
                    "type": "writing_final_response",
                    "content": chunk.content,
                }
            )

    return {
        "messages": [AIMessage(content=full_response)],
    }


def writing_review_router(
    state: RyujinState,
) -> Literal["reviser", "finalizer"]:
    if (
        state["writing_decision"] == "approved"
        or state["writing_iterations"] >= MAX_WRITING_REVISIONS
    ):
        return "finalizer"

    return "reviser"


builder = StateGraph(RyujinState)

builder.add_node("initialize_writing_state", initialize_writing_state)
builder.add_node("writing_planner", writing_planner)
builder.add_node("writing_worker", writing_worker)
builder.add_node("writing_reviewer", writing_reviewer)
builder.add_node("writing_reviser", writing_reviser)
builder.add_node("writing_finalizer", writing_finalizer)

builder.add_edge(START, "initialize_writing_state")
builder.add_edge("initialize_writing_state", "writing_planner")
builder.add_edge("writing_planner", "writing_worker")
builder.add_edge("writing_worker", "writing_reviewer")
builder.add_conditional_edges(
    "writing_reviewer",
    writing_review_router,
    {
        "reviser": "writing_reviser",
        "finalizer": "writing_finalizer",
    },
)
builder.add_edge("writing_reviser", "writing_reviewer")
builder.add_edge("writing_finalizer", END)

writing_graph = builder.compile()
