from datetime import datetime
import streamlit as st


# ==========================================================
# GREETING
# ==========================================================

def get_greeting():

    hour = datetime.now().hour

    if 5 <= hour < 12:
        return "Good Morning"

    elif 12 <= hour < 17:
        return "Good Afternoon"

    elif 17 <= hour < 22:
        return "Good Evening"

    return "Good Evening"


# ==========================================================
# HEADER
# ==========================================================

def render_header():

    current_thread = st.session_state.current_thread

    # Show the hero only when there is no active conversation
    if current_thread is None:
        show_header = True

    else:
        conversation = st.session_state.conversations[current_thread]
        show_header = len(conversation["messages"]) == 0

    if not show_header:
        return

    st.markdown(
        f"""
<div class="hero">

<div class="hero-title">
{get_greeting()}, Eshan 👋
</div>

<div class="hero-subtitle">
What shall we build today?
</div>

</div>
""",
        unsafe_allow_html=True,
    )