import streamlit as st

from utils.api import stream_chat


def process_pending_prompt():
    if not st.session_state.is_generating: 
        return

    prompt = st.session_state.pending_prompt

    if prompt is None:
        return

    conversation = st.session_state.conversations[
        st.session_state.current_thread
    ]

    with st.chat_message("assistant"):
        response = st.write_stream(     #displays the response from backend in chunks as it is being generated
            stream_chat(
                message=prompt,
                thread_id=conversation["thread_id"],
            )
        )

    conversation["messages"].append(    #then stores the response from backend inside the messages list of the conversation dict with role as assistant and content as the response
        { 
            "role": "assistant",
            "content": response,
        }
    )

    st.session_state.pending_prompt = None  #this makes the pending prompt to none so that it does not get processed again and again
    st.session_state.is_generating = False #this stops the chat processor from running again and again and only runs when a new prompt is given