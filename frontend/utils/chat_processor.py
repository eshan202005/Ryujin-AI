import streamlit as st
from requests.exceptions import RequestException

from utils.api import stream_chat
from utils.helpers import LOGO_IMAGE


def process_pending_prompt():
    if not st.session_state.is_generating: 
        return

    prompt = st.session_state.pending_prompt

    if prompt is None:
        st.session_state.is_generating = False
        return

    # Consume this prompt before starting I/O so a rerun cannot resubmit it.
    st.session_state.pending_prompt = None

    conversation = st.session_state.conversations[
        st.session_state.current_thread
    ]

    status = st.status("Connecting to Ryujin...", expanded=False)
    last_label = None

    def show_status(label):
        nonlocal last_label
        if label != last_label:
            status.update(label=label, state="running")
            status.write(label)
            last_label = label

    try:
        with st.chat_message("assistant", avatar=str(LOGO_IMAGE) if LOGO_IMAGE.exists() else "🐉"):
            st.markdown('<div class="assistant-label">Ryujin</div>', unsafe_allow_html=True)
            response = st.write_stream(
                stream_chat(
                    message=prompt,
                    thread_id=conversation["thread_id"],
                    on_status=show_status,
                )
            )

        conversation["messages"].append({"role": "assistant", "content": response})
        status.update(label="Response ready", state="complete", expanded=False)
    except (RequestException, RuntimeError, ValueError) as error:
        status.update(label="Response interrupted", state="error", expanded=True)
        status.write("The request could not be completed. You can send another message.")
        st.error(str(error))
    finally:
        st.session_state.is_generating = False
