import requests

BASE_URL = "http://127.0.0.1:8000"


def stream_chat(message: str, thread_id: str):
    response = requests.post(
        f"{BASE_URL}/chat/stream",
        json={
            "message": message,
            "thread_id": thread_id,
        },
        stream=True,
    )

    response.raise_for_status()

    for chunk in response.iter_content(
        chunk_size=None,
        decode_unicode=True,
    ):
        if chunk:
            yield chunk