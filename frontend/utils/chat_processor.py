import streamlit as st

from utils.api import chat


def process_pending_prompt():

    if not st.session_state.is_generating:
        return

    prompt = st.session_state.pending_prompt

    if prompt is None:
        return

    conversation = st.session_state.conversations[
        st.session_state.current_thread
    ]

    response = chat(
        message=prompt,
        thread_id=conversation["thread_id"],
    )

    conversation["messages"].append(
        {
            "role": "assistant",
            "content": response,
        }
    )

    st.session_state.pending_prompt = None
    st.session_state.is_generating = False

    st.rerun()