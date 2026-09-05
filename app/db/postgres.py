import psycopg

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from app.config import settings


async def init_db():
    conn = await psycopg.AsyncConnection.connect(
        settings.DATABASE_URL,
        autocommit=True
    )

    checkpointer = AsyncPostgresSaver(conn)

    await checkpointer.setup()

    return checkpointer, conn