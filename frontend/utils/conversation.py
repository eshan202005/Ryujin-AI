import streamlit as st
import uuid
def create_conversation():

    thread_id = str(uuid.uuid4())

    conversation = {
        "thread_id": thread_id,
        "name": "New Chat",
        "messages": [],
        "files": [],
    }

    st.session_state.conversations[thread_id] = conversation

    st.session_state.current_thread = thread_id