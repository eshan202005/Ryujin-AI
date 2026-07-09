import streamlit as st


WELCOME_MESSAGE = """
# 👋 Welcome to Ryujin AI

I'm your **intelligent multi-agent AI assistant**.

Soon I'll be able to:

- 🧠 Route tasks using a LangGraph Supervisor
- 📄 Chat with your uploaded documents
- 🌐 Search the web
- 🧩 Use tools dynamically
- 💾 Remember previous conversations
- ⚡ Stream responses in real time

Ask me anything to get started.
"""


def initialize_chat():

    if "messages" not in st.session_state:

        st.session_state.messages = [
            {
                "role": "assistant",
                "content": WELCOME_MESSAGE,
            }
        ]


def render_chat():

    initialize_chat()

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):

            st.markdown(message["content"])