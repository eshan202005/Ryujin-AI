import streamlit as st


from utils.helpers import (
    load_css,
    set_background,
)

from components.sidebar import render_sidebar
from components.header import render_header
from components.chat import render_chat
from components.input import render_input
from utils.chat_processor import process_pending_prompt


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

if "conversations" not in st.session_state:
    st.session_state.conversations = {}

if "current_thread" not in st.session_state:
    st.session_state.current_thread = None

if "is_generating" not in st.session_state:
    st.session_state.is_generating = False
if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None
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
process_pending_prompt()