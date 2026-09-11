from backend.graphs.checkpointer import (
    checkpointer,
    run_async,
)


async def _load_persisted_conversations():

    latest_checkpoints = {}

    # Get all saved checkpoints
    async for checkpoint in checkpointer.alist(None):

        config = checkpoint.config

        thread_id = config["configurable"].get("thread_id")

        if not thread_id:
            continue

        # Keep only the latest checkpoint for each thread
        existing = latest_checkpoints.get(thread_id)

        if existing is None or checkpoint.checkpoint["ts"] > existing.checkpoint["ts"]:
            latest_checkpoints[thread_id] = checkpoint

    conversations = {}

    # Convert LangGraph data into frontend format
    for thread_id, checkpoint in latest_checkpoints.items():

        checkpoint_data = checkpoint.checkpoint

        messages = checkpoint_data.get(
            "channel_values",
            {},
        ).get(
            "messages",
            [],
        )

        # Find first user message
        name = "New Chat"

        for message in messages:

            if message.type == "human":

                name = message.content.strip()

                # Keep sidebar names reasonably short
                if len(name) > 40:
                    name = name[:40] + "..."

                break

        conversations[thread_id] = {
            "thread_id": thread_id,
            "name": name,
            "messages": [
                {
                    "role": (
                        "user"
                        if message.type == "human"
                        else "assistant"
                    ),
                    "content": message.content,
                }
                for message in messages
            ],
            "files": [],
        }

    return conversations


def load_persisted_conversations():

    return run_async(
        _load_persisted_conversations()
    )