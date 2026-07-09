import streamlit as st


def render_input():

    prompt = st.chat_input(
        "Ask Ryujin anything..."
    )

    if not prompt:
        return

    # -------------------------
    # User
    # -------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": prompt,
        }
    )

    # -------------------------
    # Temporary AI Response
    # -------------------------

    response = f"""
You asked:

> {prompt}

🚧 Ryujin's backend is still under development.

Soon this request will flow through:

User

↓

FastAPI

↓

LangGraph Supervisor

↓

Selected Agent

↓

Streaming Response
"""

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": response,
        }
    )

    st.rerun()