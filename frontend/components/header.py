from datetime import datetime
from html import escape
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
        st.markdown(
            f'<div class="conversation-heading"><h1>{escape(str(conversation["name"]))}</h1>'
            '<p>Your AI workspace</p></div>',
            unsafe_allow_html=True,
        )
        return

    st.markdown(
        f"""
<div class="hero">

<div class="hero-title">
{get_greeting()}
</div>

<div class="hero-subtitle">
What would you like to create today?
</div>

</div>
""",
        unsafe_allow_html=True,
    )
