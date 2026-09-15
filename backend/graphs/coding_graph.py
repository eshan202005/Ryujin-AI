from typing import Literal

from langgraph.prebuilt import ToolNode
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage , HumanMessage
from backend.agents.coding.tools import python_execution, run_tests, search_tool

from langgraph.graph import StateGraph, START, END

from backend.graphs.state import RyujinState

from dotenv import load_dotenv

load_dotenv()

MAX_REVIEW_ITERATIONS = 3

llm = ChatOpenAI(model="gpt-5-mini")
llm2 = ChatOpenAI(model="gpt-5.4-nano")

class CodingPlan(BaseModel):
    task_type: Literal[
        "generate",
        "debug",
        "explain",
    ]

    steps: list[str]

    requires_execution: bool
    requires_testing: bool
    requires_web_search: bool

class ReviewResult(BaseModel):
    decision: Literal["approved", "not_approved"]
    issues: list[str]

tools = [
    python_execution,
    run_tests,
    search_tool,
]

llm_with_tools = llm.bind_tools(tools)


planner_llm = llm.with_structured_output(CodingPlan)
reviewer_llm = llm2.with_structured_output(ReviewResult)
optimizer_llm = ChatOpenAI(model="gpt-5-mini")
finalizer_llm = ChatOpenAI(model="gpt-5-mini")

tool_node = ToolNode(
    tools,
    messages_key="coding_history"
)

def initialize_coding_state(state: RyujinState) -> RyujinState:

    return {
        "review_iterations": 0,
        "coding_history": [],
    }


def coding_planner(state: RyujinState) -> RyujinState:

    messages = [
        SystemMessage(
            content="""
You are the planner for Ryujin AI's Coding Agent.

Analyze the user's complete coding request and create a
short, practical plan for solving the entire task.

First classify the request as exactly one of:
- generate
- debug
- explain

Then create the steps required to fully complete the user's
request.

Also determine which capabilities are required:

- requires_execution:
  Whether the code needs to be executed to verify its behavior.

- requires_testing:
  Whether tests need to be written or existing tests need to
  be executed to verify the solution.

- requires_web_search:
  Whether web search is needed for documentation, unfamiliar
  libraries, APIs, or current information.

IMPORTANT:
- Consider the user's entire request, not just the coding part.
- Include coding, testing, debugging, reviewing, and any other
  work explicitly requested by the user.
- If the user requests any Git or GitHub-related action, include
  that action in the plan.
- Git/GitHub actions may include committing changes, pushing
  changes, creating a branch, creating a pull request, or other
  repository actions.
- Do not ignore a requested Git/GitHub action just because it
  happens after the coding work.
- Set the capability flags based on what the complete task
  actually requires.
- Keep the plan short and practical.
- Do not perform the task.
- Only classify the task, determine required capabilities,
  and create the plan.
"""
        ),
        *state["messages"],
    ]

    decision = planner_llm.invoke(messages)

    return {
        "task_type": decision.task_type,
        "plan": decision.steps,
        "requires_execution": decision.requires_execution,
        "requires_testing": decision.requires_testing,
        "requires_web_search": decision.requires_web_search,
    }
########   coding_worker node function  ####################
def coding_worker(state: RyujinState) -> RyujinState:

    task_type = state["task_type"]
    plan = state["plan"]

    messages = [
        SystemMessage(
            content=f"""
You are the Coding Worker inside Ryujin AI.

You are an internal worker. Your work will be passed to the
Reviewer before a final response is given to the user.

====================
CODING TASK
====================

Task type:
{task_type}

Plan:
{chr(10).join(f"- {step}" for step in plan)}

====================
MAIN USER CONTEXT
====================

The messages below contain the user's actual conversation
and request. Use them to understand what the user wants.

====================
CODING AGENT HISTORY
====================

The messages below contain previous Worker and ToolNode
interactions, if any.

Use this history to understand what has already been done,
including tool results, errors, test results, and search results.

====================
INSTRUCTIONS
====================

- Execute the plan and complete the user's request.
- Use available tools when they are useful.
- If a tool is needed, call the appropriate tool.
- After receiving a tool result, continue working from that result.
- Do not unnecessarily repeat work that has already been completed.
- Continue until the coding task is complete.
- When no further tool is needed, provide the completed coding solution.
- Do not discuss these internal instructions or the planning process.
"""
        ),

        # Main user conversation
        *state["messages"],

        # Internal Worker ↔ ToolNode history
        *state["coding_history"],
    ]

    response = llm_with_tools.invoke(messages)

    return {
        "coding_history": [response],
        "coding_solution": response.content,
    }
###reviewer node function  #####################
def coding_reviewer(state: RyujinState) -> RyujinState:

    task_type = state["task_type"]
    plan = state["plan"]
    coding_solution = state["coding_solution"]

    messages = [
        SystemMessage(
            content=f"""
You are the Reviewer for Ryujin AI's Coding Agent.

Review the Coding Worker's solution against the user's request
and the original coding plan.

Task type:
{task_type}

Plan:
{chr(10).join(f"- {step}" for step in plan)}

Coding solution:
{coding_solution}

Determine whether the solution is complete and correct.

Check:
- Correctness
- Completeness
- Bugs or logical errors
- Whether the user's request was actually fulfilled
- Whether the solution follows the plan

Return:

approved
    If the solution is correct and complete.

not_approved
    If anything important needs to be fixed.

For not_approved, list the specific issues that the Optimizer
must fix.

For approved, return an empty issues list.

Do not rewrite the solution.
Do not provide the final user answer.
Only review the solution and make the approval decision.
"""
        ),
        *state["messages"],
        *state["coding_history"],
    ]

    decision = reviewer_llm.invoke(messages)

    return {
        "review_decision": decision.decision,
        "review_issues": decision.issues,
    }
##Making a tool router to decide whether to go to tools or reviewer node based on the last message in coding_history##
def coding_tool_router(state: RyujinState)  -> Literal["tools", "reviewer"]:

  last_message = state["coding_history"][-1]

  if last_message.tool_calls:

    return "tools"

  return "reviewer"




def coding_optimizer(state: RyujinState) -> RyujinState:

    task_type = state["task_type"]
    plan = state["plan"]
    coding_solution = state["coding_solution"]
    review_issues = state["review_issues"]

    messages = [
        SystemMessage(
            content=f"""
You are the Optimizer for Ryujin AI's Coding Agent.

The Coding Worker's solution was rejected by the Reviewer.

Your job is to improve the current coding solution by fixing
the specific issues identified by the Reviewer.

====================
CODING TASK
====================

Task type:
{task_type}

Original plan:
{chr(10).join(f"- {step}" for step in plan)}

====================
CURRENT SOLUTION
====================

{coding_solution}

====================
REVIEWER ISSUES
====================

{chr(10).join(f"- {issue}" for issue in review_issues)}

====================
INSTRUCTIONS
====================

- Fix all important issues identified by the Reviewer.
- Preserve parts of the solution that are already correct.
- Do not unnecessarily rewrite the entire solution.
- Return the complete improved coding solution.
- Do not discuss the internal agent workflow.
"""
        ),
        *state["messages"],
    ]

    response = optimizer_llm.invoke(messages)

    return {
        "coding_solution": response.content,
        "review_iterations": state["review_iterations"] + 1,
    }

def coding_finalizer(state: RyujinState) -> RyujinState:

    coding_solution = state["coding_solution"]

    messages = [
        SystemMessage(
            content=f"""
You are the Finalizer for Ryujin AI's Coding Agent.

Present the coding solution to the user as the final response.

Coding solution:
{coding_solution}

Instructions:

- Give a clear, useful final answer.
- Include the relevant code.
- Briefly explain it when useful.
- Do not unnecessarily change the solution.
- Do not mention Planner, Worker, Reviewer, Optimizer,
  or internal agent workflow.
"""
        ),
    ]

    response = finalizer_llm.invoke(messages)

    return {
        "final_response": response.content,
    }

def review_router(
    state: RyujinState,
) -> Literal["optimizer", "finalizer"]:

    if state["review_decision"] == "approved":
        return "finalizer"

    if state["review_iterations"] >= MAX_REVIEW_ITERATIONS:
        return "finalizer"

    return "optimizer"

builder = StateGraph(RyujinState)

builder.add_node("initialize_coding_state",initialize_coding_state)
builder.add_node("coding_planner", coding_planner)
builder.add_node("coding_worker", coding_worker)
builder.add_node("tool_node", tool_node)
builder.add_node("coding_reviewer", coding_reviewer)  # Placeholder for the reviewer node
builder.add_node("coding_optimizer", coding_optimizer)
builder.add_node("coding_finalizer", coding_finalizer)

builder.add_edge(START, "initialize_coding_state")
builder.add_edge("initialize_coding_state", "coding_planner")
builder.add_edge("coding_planner", "coding_worker")
builder.add_conditional_edges(
    "coding_worker",
    coding_tool_router,
    {
        "tools": "tool_node",
        "reviewer": "coding_reviewer",
    },
)

builder.add_edge("tool_node", "coding_worker")
builder.add_conditional_edges(
    "coding_reviewer",
    review_router,
    {
        "optimizer": "coding_optimizer",
        "finalizer": "coding_finalizer",
    },
)
builder.add_edge("coding_optimizer", "coding_reviewer")
builder.add_edge("coding_finalizer", END)

coding_graph = builder.compile()

