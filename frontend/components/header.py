from datetime import datetime
import streamlit as st


def get_greeting():

    hour = datetime.now().hour

    if 5 <= hour < 12:
        greeting = "Good Morning"

    elif 12 <= hour < 17:
        greeting = "Good Afternoon"

    elif 17 <= hour < 22:
        greeting = "Good Evening"

    else:
        greeting = "Good Evening"

    return greeting


def render_header():

    if len(st.session_state.messages) > 0:
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