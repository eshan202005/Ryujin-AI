import streamlit as st

from utils.helpers import show_logo
from utils.api import upload_file


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
    # DOCUMENTS
    # ======================================================

    st.markdown(
        '<div class="sidebar-section">DOCUMENTS</div>',
        unsafe_allow_html=True,
    )


    # ======================================================
    # CURRENT CONVERSATION
    # ======================================================

    current_thread = st.session_state.current_thread

    conversation = st.session_state.conversations.get(
        current_thread
    )


    # ======================================================
    # UPLOAD
    # ======================================================

    uploaded_file = st.file_uploader(
        "Upload document",
        type=["pdf"],
        label_visibility="collapsed",
        key="document_uploader",
    )


    if uploaded_file is not None:

        if current_thread is None:

            st.info(
                "Start a chat before uploading a document."
            )

        else:

            if st.button(
                "📎  Upload Document",
                use_container_width=True,
                key="upload_document_button",
            ):

                with st.spinner(
                    "Processing document..."
                ):

                    # Send the file AND the current
                    # conversation's thread_id
                    result = upload_file(
                        uploaded_file,
                        current_thread,
                    )


                    # ======================================
                    # UPDATE FRONTEND CONVERSATION
                    # ======================================

                    conversation["files"].append(
                        {
                            "file_id": result["file_id"],
                            "filename": result["filename"],
                            "file_type": result["file_type"],
                        }
                    )


                st.success(
                    "Document uploaded!"
                )

                st.rerun()


    # ======================================================
    # CURRENT CHAT'S DOCUMENTS
    # ======================================================

    if conversation:

        files = conversation.get(
            "files",
            []
        )

        if files:

            for file in files:

                st.html(
                    f"""
                    <div class="file-card">

                        <span class="file-icon">
                            📄
                        </span>

                        <span class="file-name">
                            {file["filename"]}
                        </span>

                    </div>
                    """
                )


    st.markdown("<hr>", unsafe_allow_html=True)


    # ======================================================
    # CONVERSATIONS
    # ======================================================

    st.markdown(
        '<div class="sidebar-section">CONVERSATIONS</div>',
        unsafe_allow_html=True,
    )


    # ======================================================
    # EMPTY STATE
    # ======================================================

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
    # CONVERSATIONS
    # ======================================================

    # persistence.py already sorts these
    # oldest → newest, so don't reverse them here.

    for thread_id, conversation in (
        st.session_state.conversations.items()
    ):

        is_active = (
            thread_id
            == st.session_state.current_thread
        )


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