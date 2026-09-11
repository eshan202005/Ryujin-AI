import streamlit as st
from utils.conversation import create_conversation
from utils.helpers import show_logo



def render_sidebar():
    

    # ======================================================
    # LOGO
    # ======================================================

    logo, text = st.columns(
        [1.35, 2.65],
        gap="small",
        vertical_alignment="center",
    )

    with logo:
        show_logo(width=90)

    with text:

        st.markdown(
            """
<div class="logo-title">
RYUJIN <span class="logo-ai">AI</span>
</div>
""",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
<div class="logo-subtitle">
Building Intelligence
</div>
""",
            unsafe_allow_html=True,
        )

    st.write("")

    # ======================================================
    # NEW CHAT
    # ======================================================

    if st.button( #when new chat button pressed current thread = none and rerun the app
        "➕  New Chat",
        use_container_width=True,
        type="primary",
    ):
        st.session_state.current_thread = None
        st.rerun()

    st.markdown("<hr>", unsafe_allow_html=True)

    # ======================================================
    # CONVERSATIONS
    # ======================================================

    st.markdown(
        '<div class="sidebar-section">CONVERSATIONS</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.conversations:

        st.markdown(
        """
<div class="empty-card">

<b>No conversations yet.</b>

<br><br>

Start a new chat to begin.

</div>
""",
        unsafe_allow_html=True,
    )

    else:

        for thread_id, conversation in reversed(st.session_state.conversations.items()): #this displays all the previous chats 

            if st.button( #when a old chat is pressed it sets current thread to that the thread id of that old chat and reruns the app to display that chat
            conversation["name"],
            key=f"conversation_{thread_id}",
            use_container_width=True,
            ):

                st.session_state.current_thread = thread_id

                st.rerun()