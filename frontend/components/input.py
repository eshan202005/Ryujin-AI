import streamlit as st


from utils.conversation import create_conversation


import streamlit as st
from utils.conversation import create_conversation


def render_input():#takes input from user 

    prompt = st.chat_input(
        "Ask Ryujin anything...",
        disabled=st.session_state.is_generating,
    )

    if prompt: #if input is given 

        if st.session_state.current_thread is None:

            create_conversation() # this creates a new thread_id and makea a dict named conversation with contains that thead_id, name, messages
            #and then store them into the session state coversations with thread_id as the key and conversations dict as its values

            conversation = st.session_state.conversations[
                st.session_state.current_thread
            ]

            # Use the first message as the conversation name
            conversation["name"] = prompt[:40]

            if len(prompt) > 40:
                conversation["name"] += "..."

        conversation = st.session_state.conversations[
            st.session_state.current_thread
        ]

        conversation["messages"].append(  #stores the first input message inside the messages list of the conversation dict
            # with role as user and content as the prompt
            {
                "role": "user",
                "content": prompt,
            }
        )

        st.session_state.pending_prompt = prompt 
        st.session_state.is_generating = True #makes the generating true so that chat_prosseror works
        

        st.rerun()