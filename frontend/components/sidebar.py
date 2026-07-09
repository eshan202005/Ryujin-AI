import streamlit as st
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
        show_logo(width=80)

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

    st.button(
        "➕  New Chat",
        use_container_width=True,
        type="primary",
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ======================================================
    # CONVERSATIONS
    # ======================================================

    st.markdown(
        '<div class="sidebar-section">CONVERSATIONS</div>',
        unsafe_allow_html=True,
    )

    if not st.session_state.threads:

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

    st.markdown("<hr>", unsafe_allow_html=True)

    # ======================================================
    # WORKSPACE
    # ======================================================

    st.markdown(
        '<div class="sidebar-section">WORKSPACE</div>',
        unsafe_allow_html=True,
    )

    st.button(
        "📄 Upload Resume",
        use_container_width=True,
        key="upload_resume",
    )

    st.markdown("<hr>", unsafe_allow_html=True)

    # ======================================================
    # SETTINGS
    # ======================================================

    st.markdown(
        '<div class="sidebar-section">SETTINGS</div>',
        unsafe_allow_html=True,
    )

    st.caption("Coming Soon")