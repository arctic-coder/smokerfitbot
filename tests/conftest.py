import asyncio
import logging
import os

import asyncpg
import pytest

from db import init_db

log = logging.getLogger(__name__)

TEST_DB_DSN = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/smokerfit_test",
)

_pg_pool_instance = None
_pg_available = None


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def pg_pool():
    global _pg_pool_instance, _pg_available
    try:
        pool = await asyncpg.create_pool(dsn=TEST_DB_DSN, min_size=1, max_size=5)
        os.environ["DATABASE_URL"] = TEST_DB_DSN
        await init_db()
        _pg_pool_instance = pool
        _pg_available = True
        yield pool
        await pool.close()
    except Exception as exc:
        log.warning("Could not connect to test PostgreSQL (%s). DB-dependent tests will be skipped.", exc)
        _pg_available = False
        yield None


@pytest.fixture(autouse=True)
async def _db_clean(pg_pool):
    if pg_pool is None:
        yield
        return
    async with pg_pool.acquire() as conn:
        await conn.execute("TRUNCATE users, subscriptions, payments, promocodes RESTART IDENTITY CASCADE")
    yield


def requires_db(fn):
    """Decorator to skip a test if the test DB is unavailable."""
    return pytest.mark.skipif(
        not _pg_available if _pg_available is not None else True,
        reason="Test PostgreSQL not available",
    )(fn)
