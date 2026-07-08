import asyncio
import threading

import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

_ASYNC_LOOP = asyncio.new_event_loop()

_ASYNC_THREAD = threading.Thread(
    target=_ASYNC_LOOP.run_forever,
    daemon=True,
)

_ASYNC_THREAD.start()

def run_async(coro):
    return asyncio.run_coroutine_threadsafe(
        coro,
        _ASYNC_LOOP,
    ).result()

async def _init_checkpointer():

    conn = await aiosqlite.connect("ryujin.db")

    checkpointer = AsyncSqliteSaver(conn)

    return checkpointer

checkpointer = run_async(_init_checkpointer())

