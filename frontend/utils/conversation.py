import streamlit as st
import uuid
def create_conversation(): #creates a new  thread and a dict named conversation with contains that thead_id, name, messages and files and then store them into the session state coversations with thread_id as the key and conversations dict as its values

    thread_id = str(uuid.uuid4())

    conversation = {
        "thread_id": thread_id,
        "name": "New Chat",
        "messages": [],
        "files": [],
    }

    st.session_state.conversations[thread_id] = conversation

    st.session_state.current_thread = thread_id  #and also stores current_thread = thread_id created 