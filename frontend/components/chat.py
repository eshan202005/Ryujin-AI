import streamlit as st


# ==========================================================
# WELCOME SCREEN
# ==========================================================

def render_welcome():

    st.markdown(
        """
<div class="welcome-card">

<h2>Welcome to Ryujin AI</h2>

<p class="welcome-subtitle">
Your intelligent multi-agent assistant.
</p>

<p class="welcome-description">
Ryujin automatically selects the best agents and tools
for every request.
</p>

<div class="capability-list">

<div class="capability-item">
🧠 <span>Research</span>
</div>

<div class="capability-item">
💻 <span>Coding</span>
</div>

<div class="capability-item">
📄 <span>Resume Chat</span>
</div>

<div class="capability-item">
🌐 <span>Web Search</span>
</div>

<div class="capability-item">
⚡ <span>AI Workflows</span>
</div>

</div>

</div>
""",
        unsafe_allow_html=True,
    )
# ==========================================================
# CHAT MESSAGES
# ==========================================================

def render_messages():

    for message in st.session_state.messages:

        avatar = "👤" if message["role"] == "user" else "🐉"

        with st.chat_message(
            message["role"],
            avatar=avatar,
        ):

            st.markdown(message["content"])


# ==========================================================
# MAIN CHAT
# ==========================================================

def render_chat():

    if len(st.session_state.messages) == 0:

        render_welcome()

    render_messages()