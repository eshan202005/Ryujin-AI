from html import escape

import streamlit as st

from utils.helpers import show_logo
from utils.api import upload_file


def render_sidebar():
    with st.container(key="sidebar_brand"):
        logo, text = st.columns([1.05, 3], gap="small", vertical_alignment="center")
        with logo:
            show_logo(width=60)
        with text:
            st.markdown(
                '<div class="logo-title">RYUJIN <span class="logo-ai">AI</span></div>'
                '<div class="logo-subtitle">Your AI workspace</div>',
                unsafe_allow_html=True,
            )

        if st.button("＋ New chat", use_container_width=True, type="primary"):
            st.session_state.current_thread = None
            st.rerun()

    st.markdown('<div class="sidebar-section">CONVERSATIONS</div>', unsafe_allow_html=True)

    # Keep Documents in place regardless of the number of conversations.
    with st.container(height=280, border=False, key="sidebar_conversations"):
        if not st.session_state.conversations:
            st.markdown(
                '<div class="sidebar-empty">No conversations yet.<br>'
                'Start a new chat to begin.</div>',
                unsafe_allow_html=True,
            )

        for thread_id, conversation in st.session_state.conversations.items():
            if st.button(
                conversation["name"],
                key=f"conversation_{thread_id}",
                use_container_width=True,
                type="primary" if thread_id == st.session_state.current_thread else "secondary",
                icon=":material/chat_bubble_outline:",
            ):
                st.session_state.current_thread = thread_id
                st.rerun()

    current_thread = st.session_state.current_thread
    conversation = st.session_state.conversations.get(current_thread)

    with st.container(key="sidebar_documents"):
        st.markdown('<div class="sidebar-section">DOCUMENTS</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Upload a PDF",
            type=["pdf"],
            label_visibility="collapsed",
            key="document_uploader",
        )

        if uploaded_file is not None:
            if current_thread is None:
                st.info("Start a chat before uploading a document.")
            elif st.button(
                "📎 Upload Document",
                use_container_width=True,
                key="upload_document_button",
            ):
                with st.spinner("Processing document..."):
                    result = upload_file(uploaded_file, current_thread)
                    conversation["files"].append(
                        {
                            "file_id": result["file_id"],
                            "filename": result["filename"],
                            "file_type": result["file_type"],
                        }
                    )
                st.success("Document uploaded!")
                st.rerun()

        files = conversation.get("files", []) if conversation else []
        if files:
            with st.container(height=120, border=False, key="sidebar_files"):
                for file in files:
                    st.html(
                        '<div class="file-card"><span class="file-icon">📄</span>'
                        f'<span class="file-name">{escape(str(file["filename"]))}</span></div>'
                    )

        st.markdown(
            '<div class="sidebar-document-note">Documents stay with this chat.</div>',
            unsafe_allow_html=True,
        )
