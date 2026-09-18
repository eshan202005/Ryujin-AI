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