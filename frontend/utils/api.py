import os
import json

import requests

BASE_URL = os.getenv("RYUJIN_API_URL", "http://127.0.0.1:8001").rstrip("/")


def stream_chat(message: str, thread_id: str, on_status=None):
    with requests.post(
        f"{BASE_URL}/chat/stream",
        json={
            "message": message,
            "thread_id": thread_id,
            "include_status": on_status is not None,
        },
        stream=True,
        timeout=(15, 180),
    ) as response:

        response.raise_for_status()

        # Preserve compatibility while Render and Streamlit update separately.
        if "application/x-ndjson" not in response.headers.get("Content-Type", ""):
            if on_status:
                on_status("Ryujin is preparing a response...")
            for chunk in response.iter_content(chunk_size=None, decode_unicode=True):
                if chunk:
                    yield chunk
            return

        response.encoding = "utf-8"
        complete = False
        for line in response.iter_lines(chunk_size=1, decode_unicode=True):
            if not line:
                continue
            event = json.loads(line)
            if event["type"] == "status" and on_status:
                on_status(event["label"])
            elif event["type"] == "token":
                yield event["content"]
            elif event["type"] == "error":
                raise RuntimeError(event["message"])
            elif event["type"] == "done":
                complete = True
        if not complete:
            raise RuntimeError("The connection ended before the response completed. Please try again.")


def upload_file(file, thread_id: str):

    response = requests.post(
        f"{BASE_URL}/files/upload",
        data={
            "thread_id": thread_id, #sends thread_id which it so the the files data can be associated in that thread_id state in the graph
        },
        files={
            "file": (
                file.name,
                file.getvalue(),
                file.type,
            )
        },
    )

    response.raise_for_status()

    return response.json()# GETS THE RESPONSE
