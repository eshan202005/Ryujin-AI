from typing import Literal

from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage

from langgraph.graph import StateGraph, START, END

from backend.graphs.state import RyujinState

from dotenv import load_dotenv

load_dotenv()


llm = ChatOpenAI(model="gpt-5-mini")

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


planner_llm = llm.with_structured_output(CodingPlan)


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
You are the Coding Worker for Ryujin AI.

Task type:
{task_type}

Plan:
{chr(10).join(f"- {step}" for step in plan)}

Execute the plan and complete the user's request.
Use the available tools when they are useful.
"""
        ),
        *state["messages"],
    ]

    response = llm.invoke(messages)

    return {
        "coding_result": response.content,
    }
    


builder = StateGraph(RyujinState)

builder.add_node("coding_planner", coding_planner)
builder.add_node("coding_worker", coding_worker)

builder.add_edge(START, "coding_planner")
builder.add_edge("coding_planner", "coding_worker")
builder.add_edge("coding_worker", END)

coding_graph = builder.compile()