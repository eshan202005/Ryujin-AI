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

    if st.button(
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

        return


    # ======================================================
    # NEWEST → OLDEST
    #
    # persistence.py stores them oldest → newest.
    # Reversing gives newest → oldest.
    #
    # This also works for newly-created conversations
    # because conversation.py adds them to the dictionary
    # in creation order.
    # ======================================================

    for thread_id, conversation in reversed(
        list(st.session_state.conversations.items())
    ):

        is_active = (
            thread_id == st.session_state.current_thread
        )


        # Active conversation gets primary styling
        button_type = (
            "primary"
            if is_active
            else "secondary"
        )


        # ==================================================
        # CONVERSATION BUTTON
        # ==================================================

        if st.button(
            conversation["name"],
            key=f"conversation_{thread_id}",
            use_container_width=True,
            type=button_type,
        ):

            st.session_state.current_thread = thread_id

            st.rerun()