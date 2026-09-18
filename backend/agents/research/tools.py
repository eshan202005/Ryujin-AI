from langchain_core.tools import tool
from typing import Annotated

from langgraph.prebuilt import InjectedState
from backend.graphs import state
from backend.rag.vector_store import vector_store
from langchain_community.tools import  DuckDuckGoSearchRun ,  WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper
from backend.rag.vector_store import get_file_retriever

@tool
def rag_search(
    query: str,
    state: Annotated[dict, InjectedState], #injected state is used to access the state rather then taking file ids from llm 
) -> str:
    """
    Search the uploaded documents belonging to the current conversation.
    """
    file_ids = [
        file["file_id"] ##this is used to get the file ids from the state 
        for file in state["files"]
    ]

    if not file_ids:
        return "No documents have been uploaded in this conversation."

    retriever = get_file_retriever(file_ids)# used to retreive the chuncks which have same file ids in meta data as the file_ids passed to the function

    results = retriever.invoke(query)

    if not results:
        return "No relevant information found in the uploaded documents."

    return "\n\n".join(
        [
            f"Source: {doc.metadata.get('file_name', 'Unknown')}\n"
            f"{doc.page_content}"
            for doc in results
        ]
    )

search_tool = DuckDuckGoSearchRun()    

wikipedia_tool = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(
        top_k_results=2,
        doc_content_chars_max=4000,
    )
)
