from langgraph.graph import StateGraph , START,END
from langchain_openai import ChatOpenAI
from backend.graphs.state import RyujinState
from backend.graphs.checkpointer import checkpointer
from dotenv import load_dotenv

load_dotenv()

llm = ChatOpenAI(model="gpt-5-mini")

def chat_agent(state: RyujinState) -> RyujinState:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

builder = StateGraph(RyujinState)

builder.add_node("chat_agent",chat_agent)
builder.add_edge(START,"chat_agent")
builder.add_edge("chat_agent",END)

chat_graph = builder.compile(checkpointer = checkpointer)

