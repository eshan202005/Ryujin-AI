from fastapi import APIRouter, UploadFile, File, Form
from pathlib import Path
import shutil
import uuid

from backend.rag.loader import load_document
from backend.rag.splitter import split_documents
from backend.rag.vector_store import vector_store
from backend.graphs.main_graph import main_graph


file_router = APIRouter()

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@file_router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    thread_id: str = Form(...),
):

    file_id = str(uuid.uuid4())

    file_path = UPLOAD_DIR / file.filename

    # 1. Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2. Load document
    documents = load_document(str(file_path))

    # 3. Split document
    chunks = split_documents(documents)

    # 4. Add metadata
    for chunk in chunks:
        chunk.metadata["file_id"] = file_id
        chunk.metadata["file_name"] = file.filename
        chunk.metadata["file_type"] = file.content_type

    # 5. Store chunks in Chroma
    vector_store.add_documents(chunks)

    # 6. File metadata for this conversation
    file_metadata = {
        "file_id": file_id,
        "filename": file.filename,
        "file_type": file.content_type,
    }

    # 7. Identify the current LangGraph conversation
    config = {
        "configurable": {
            "thread_id": thread_id
        }
    }

    # 8. Get existing files for this thread
    current_state = await main_graph.aget_state(config)

    existing_files = []

    if current_state.values:
        existing_files = current_state.values.get("files", [])

    # 9. Add this file to the thread's file list
    updated_files = [
        *existing_files,
        file_metadata,
    ]

    # 10. Persist the file list in LangGraph state
    await main_graph.aupdate_state(
        config,
        {
            "files": updated_files
        },
    )

    return {
        "file_id": file_id,
        "filename": file.filename,
        "chunks": len(chunks),
        "file_type": file.content_type,
    }
#in simples words the second part of the code just addes the files data into the files state in the 
# thread_id  given so taht the files data reaces the garaph
