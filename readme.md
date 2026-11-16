# 🐉 Ryujin AI

Ryujin AI is a Python-based multi-agent assistant with a Streamlit interface, a FastAPI backend, and LangGraph workflows. It routes requests to general, coding, or research agents and can use tools or search uploaded PDFs, depending on the task.

## Current features

- **Streaming chat** through the Streamlit frontend and FastAPI backend.
- **Conversation persistence** using LangGraph checkpoints stored in SQLite, with conversations restored in the sidebar.
- **Agent routing** through a supervisor that selects a general, coding, or research workflow.
- **General assistant tools:** calculator, unit conversion, current date and time, web search, and Wikipedia lookup.
- **Coding assistant:** code generation, debugging, and explanation, with Python execution, test-command, and web-search tools. The workflow includes planning and review steps.
- **Research assistant:** research planning and review, with web search, Wikipedia, and retrieval from PDFs uploaded to the active conversation.
- **PDF upload and retrieval:** documents are split into chunks and stored in Chroma with file metadata. Retrieval filters by the file IDs associated with the current conversation.
- **Custom Streamlit UI:** Ryujin theme, chat interface, conversation sidebar, and document list.

## Tech stack

- **Language:** Python
- **Frontend:** Streamlit
- **Backend / API:** FastAPI
- **Agent workflows:** LangGraph and LangChain
- **Language models and embeddings:** LangChain OpenAI integrations
- **Conversation checkpoints:** SQLite
- **Document vector store:** Chroma

## Project structure

```text
backend/
  agents/       Agent tools for general, coding, and research tasks
  graphs/       LangGraph workflows, shared state, and checkpoint setup
  rag/          PDF loading, chunking, embeddings, and vector retrieval
  routers/      FastAPI routes for chat and file upload
  services/     Chat and streaming orchestration
frontend/
  components/   Streamlit chat, input, header, and sidebar
  styles/       UI stylesheets
  utils/        API calls, conversation state, and persistence helpers
```

## Running locally

Install the Python packages used by the project, set `OPENAI_API_KEY` in your environment, then start the backend and frontend in separate terminals from the project root:

```bash
uvicorn backend.main:app --reload
```

```bash
streamlit run frontend/app.py
```

The frontend sends API requests to `http://127.0.0.1:8000`. The current code does not include a dependency manifest, so install the project’s required packages separately.

## Current development focus

The core chat, agent workflows, PDF retrieval, and persistence paths are implemented. The project is still under active development; the UI, agent feedback, error handling, and setup documentation can continue to improve.

## Longer-term direction

- Make agent activity and research sources clearer in the chat interface.
- Improve document handling and answer citations.
- Expand testing, configuration, and deployment support.
- Continue developing Ryujin as a practical assistant for research, coding, and document understanding.
