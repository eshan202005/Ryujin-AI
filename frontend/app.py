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
from utils.persistence import load_persisted_conversations


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
    st.session_state.conversations = load_persisted_conversations()
   

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

render_header() #renders the header whenever reuns 
render_chat() #renders the chat interface, including the welcome screen and old messages
process_pending_prompt() #processes the pending prompt and displays the response from backend in chunks as it is being generated and then stores the response inside the messages list of the conversation dict
render_input() # takes the input as its the last thing and it makes genrating =true  then reruns the app so that chat_genrator can work
# and display the response from backend in chunks as it is being generated and then stores the response inside the messages list of the conversation dict
