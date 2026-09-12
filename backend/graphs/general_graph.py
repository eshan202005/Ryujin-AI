from langgraph.graph import StateGraph , START,END
from langchain_openai import ChatOpenAI
from backend.graphs.state import RyujinState
from backend.graphs.checkpointer import checkpointer
from dotenv import load_dotenv
from langgraph.prebuilt import ToolNode , tools_condition
from backend.agents.general.tools import calculator_tool, search_tool

load_dotenv()



llm = ChatOpenAI(model="gpt-5-mini")
tools = [calculator_tool, search_tool]
llm_with_tools = llm.bind_tools(tools)

def chat_agent(state: RyujinState) -> RyujinState:
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

builder = StateGraph(RyujinState)
tool_node = ToolNode(tools)

builder.add_node("chat_agent",chat_agent)
builder.add_node("tool_node",tool_node)



builder.add_edge(START,"chat_agent")
builder.add_conditional_edges(
    "chat_agent",
    tools_condition,
    {
        "tools": "tool_node",
        "__end__": END,
    },
)
builder.add_edge("tool_node","chat_agent")

general_graph = builder.compile(checkpointer = checkpointer)

