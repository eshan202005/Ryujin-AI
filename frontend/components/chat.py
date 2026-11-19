import streamlit as st
from utils.helpers import LOGO_IMAGE


# ==========================================================
# WELCOME SCREEN
# ==========================================================

def render_welcome():

    st.markdown(
        """
<div class="welcome-card">

<div class="welcome-eyebrow">ONE WORKSPACE. MANY POSSIBILITIES.</div>
<h2>Ideas into answers.</h2>

<p class="welcome-subtitle">
Research, code, and create with Ryujin.
</p>

<p class="welcome-description">
Bring a question, a document, or your next idea.
Ryujin selects the right agent for your request.
</p>

<div class="capability-list">

<div class="capability-item">
🧠 <span>Research</span>
</div>

<div class="capability-item">
💻 <span>Coding</span>
</div>

<div class="capability-item">
✍ <span>Writing</span>
</div>

<div class="capability-item">
🌐 <span>Web Search</span>
</div>

<div class="capability-item">
📄 <span>Document Chat</span>
</div>

</div>

</div>
""",
        unsafe_allow_html=True,
    )


# ==========================================================
# CHAT MESSAGES
# ==========================================================

def render_messages(messages): #used to render the messages in the chat window

    for message in messages:

        # Skip empty messages
        if not message["content"]:
            continue

        avatar = "👤" if message["role"] == "user" else (
            str(LOGO_IMAGE) if LOGO_IMAGE.exists() else "🐉"
        )

        with st.chat_message(
            message["role"],
            avatar=avatar,
        ):
            if message["role"] == "user":
                st.html('<span class="user-message-marker" aria-hidden="true"></span>')
            if message["role"] == "assistant":
                st.markdown('<div class="assistant-label">Ryujin</div>', unsafe_allow_html=True)
            st.markdown(message["content"])


# ==========================================================
# MAIN CHAT
# ==========================================================

def render_chat(): #Renders the chat interface, including the welcome screen and messages

    current_thread = st.session_state.current_thread

    # No conversation selected yet
    if current_thread is None:
        render_welcome()
        return

    conversation = st.session_state.conversations[current_thread]

    messages = conversation["messages"]

    # Empty conversation
    if len(messages) == 0:
        render_welcome()
        return

    # Render messages
    render_messages(messages)
