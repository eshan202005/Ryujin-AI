from datetime import datetime

import streamlit as st


def get_greeting():

    hour = datetime.now().hour

    if 5 <= hour < 12:
        return "Good Morning ☀️"

    elif 12 <= hour < 17:
        return "Good Afternoon 👋"

    elif 17 <= hour < 22:
        return "Good Evening 🌙"

    return "Working Late 🌌"


def render_header():

    st.title(get_greeting())

    st.caption(
        "What shall we build today?"
    )

    st.markdown("<br>", unsafe_allow_html=True)