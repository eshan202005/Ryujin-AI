from langchain_chroma import Chroma
from backend.rag.embeddings import embeddings

VECTOR_DB_DIR = "vector_db"

vector_store = Chroma(
    collection_name="ryujin_documents",
    embedding_function=embeddings,
    persist_directory=VECTOR_DB_DIR,
)


def add_documents(documents):
    vector_store.add_documents(documents)

def get_file_retriever(file_ids: list[str]):

    return vector_store.as_retriever( # so that we only search in the chunks which have same file ids in meta data as the file_ids passed to the function
        search_type="mmr",
        search_kwargs={
            "k": 4,
            "fetch_k": 10,
            "filter": {
                "file_id": {
                    "$in": file_ids
                }
            },
        },
    )