import asyncio
import os
import threading

from dotenv import load_dotenv
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

load_dotenv()

_DATABASE_URL = os.getenv("DATABASE_URL", "")
_pool = AsyncConnectionPool(
    conninfo=_DATABASE_URL,
    open=False,
    min_size=1,
    max_size=5,
    kwargs={
        "autocommit": True,
        "row_factory": dict_row,
        "prepare_threshold": None,
    },
)

class PostgresCheckpointer(BaseCheckpointSaver):
    """Keep graph compilation separate from async database startup."""

    saver = None

    def _ready(self):
        if self.saver is None:
            raise RuntimeError("Initialize the Postgres checkpointer before running the graph.")
        return self.saver

    async def aget_tuple(self, config):
        return await self._ready().aget_tuple(config)

    async def alist(self, config, *, filter=None, before=None, limit=None):
        async for checkpoint in self._ready().alist(
            config, filter=filter, before=before, limit=limit
        ):
            yield checkpoint

    async def aput(self, config, checkpoint, metadata, new_versions):
        return await self._ready().aput(config, checkpoint, metadata, new_versions)

    async def aput_writes(self, config, writes, task_id, task_path=""):
        return await self._ready().aput_writes(config, writes, task_id, task_path)

    async def adelete_thread(self, thread_id):
        return await self._ready().adelete_thread(thread_id)

    def get_next_version(self, current, channel):
        return self._ready().get_next_version(current, channel)


checkpointer = PostgresCheckpointer()
_initialized = False


async def initialize_checkpointer():
    global _initialized
    if _initialized:
        return
    if not _DATABASE_URL.startswith(("postgresql://", "postgres://")):
        raise RuntimeError("Set DATABASE_URL to a PostgreSQL connection URL.")
    try:
        await _pool.open(wait=True, timeout=30)
        saver = AsyncPostgresSaver(_pool)
        await saver.setup()
        checkpointer.saver = saver
    except BaseException:
        await _pool.close()
        raise
    _initialized = True


async def close_checkpointer():
    await _pool.close()


# The local Streamlit history loader uses a synchronous entry point. Its
# database operations run together on this dedicated loop in that process.

_ASYNC_LOOP = (
    asyncio.SelectorEventLoop() if os.name == "nt" else asyncio.new_event_loop()
)

_ASYNC_THREAD = threading.Thread(
    target=_ASYNC_LOOP.run_forever,
    daemon=True,
)

_ASYNC_THREAD.start()

def run_async(coro):
    async def run_with_checkpointer():
        try:
            await initialize_checkpointer()
        except BaseException:
            coro.close()
            raise
        return await coro

    return asyncio.run_coroutine_threadsafe(
        run_with_checkpointer(),
        _ASYNC_LOOP,
    ).result()

