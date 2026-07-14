import streamlit as st

from utils.api import chat
from utils.conversation import create_conversation


def render_input():

    # ======================================================
    # CHAT INPUT (Always Visible)
    # ======================================================

    prompt = st.chat_input(
    "Ask Ryujin anything...",
    disabled=st.session_state.is_generating,
    )

    # -----------------------------------------
    # User submitted a prompt
    # -----------------------------------------

    if prompt:

        if st.session_state.current_thread is None:
            create_conversation()

        conversation = st.session_state.conversations[
            st.session_state.current_thread
        ]

        conversation["messages"].append(
            {
                "role": "user",
                "content": prompt,
            }
        )

        st.session_state.pending_prompt = prompt
        st.session_state.is_generating = True

        st.rerun()