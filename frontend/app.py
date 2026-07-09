import streamlit as st

from utils.helpers import (
    load_css,
    set_background,
)

from components.sidebar import render_sidebar
from components.header import render_header
from components.chat import render_chat
from components.input import render_input


# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Ryujin AI",
    page_icon="🐉",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==========================================================
# LOAD GLOBAL STYLES
# ==========================================================

load_css()
set_background()

# ==========================================================
# SESSION STATE
# ==========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "threads" not in st.session_state:
    st.session_state.threads = []

if "current_thread" not in st.session_state:
    st.session_state.current_thread = None

# ==========================================================
# SIDEBAR
# ==========================================================

with st.sidebar:
    render_sidebar()

# ==========================================================
# MAIN PAGE
# ==========================================================

render_header()

render_chat()

render_input()