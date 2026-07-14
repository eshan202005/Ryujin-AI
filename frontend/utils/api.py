import requests


BASE_URL = "http://127.0.0.1:8000"


def chat(message: str, thread_id: str):

    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "message": message,
            "thread_id": thread_id,
        },
    )

    response.raise_for_status()

    return response.json()["response"]