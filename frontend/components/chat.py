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

def render_messages(messages):

    for message in messages:

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

    if st.session_state.is_generating:
        with st.chat_message("assistant", avatar="🐉"):
            st.spinner("Ryujin is thinking...")