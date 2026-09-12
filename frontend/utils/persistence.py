from backend.graphs.checkpointer import (
    checkpointer,
    run_async,
)


async def _load_persisted_conversations():

    threads = {}

    # ======================================================
    # READ ALL CHECKPOINTS
    # ======================================================

    async for checkpoint in checkpointer.alist(None):

        config = checkpoint.config

        thread_id = config["configurable"].get("thread_id")

        if not thread_id:
            continue

        checkpoint_data = checkpoint.checkpoint

        timestamp = checkpoint_data.get("ts")

        if not timestamp:
            continue

        # First checkpoint = conversation creation time
        # Latest checkpoint = conversation's latest state

        if thread_id not in threads:

            threads[thread_id] = {
                "created_at": timestamp,
                "latest_at": timestamp,
                "latest_checkpoint": checkpoint,
            }

        else:

            # Keep earliest timestamp for ordering
            if timestamp < threads[thread_id]["created_at"]:

                threads[thread_id]["created_at"] = timestamp

            # Keep latest checkpoint for complete history
            if timestamp > threads[thread_id]["latest_at"]:

                threads[thread_id]["latest_at"] = timestamp

                threads[thread_id]["latest_checkpoint"] = checkpoint


    conversations = {}


    # ======================================================
    # BUILD CONVERSATIONS
    # ======================================================

    for thread_id, data in threads.items():

        checkpoint_data = data["latest_checkpoint"].checkpoint

        messages = (
            checkpoint_data
            .get("channel_values", {})
            .get("messages", [])
        )


        # ==================================================
        # AUTOMATIC CHAT NAME
        # ==================================================

        name = "New Chat"

        for message in messages:

            if message.type == "human":

                name = message.content.strip()

                if len(name) > 40:

                    name = name[:40] + "..."

                break


        # ==================================================
        # FRONTEND CONVERSATION
        # ==================================================

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


    # ======================================================
    # SORT OLDEST → NEWEST
    #
    # sidebar.py reverses this when displaying,
    # giving us NEWEST → OLDEST.
    # ======================================================

    conversations = dict(
        sorted(
            conversations.items(),
            key=lambda item: threads[item[0]]["created_at"],
        )
    )


    return conversations


def load_persisted_conversations():

    return run_async(
        _load_persisted_conversations()
    )