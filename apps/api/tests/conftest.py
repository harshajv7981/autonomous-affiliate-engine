import pytest
from sqlalchemy import inspect

from db.models import Base
from db.session import SessionLocal, engine


def _postgres_available() -> bool:
    try:
        with engine.connect():
            return True
    except Exception:  # noqa: BLE001  (any connection failure means unavailable)
        return False


@pytest.fixture
def fresh_db():
    """Reset the domain schema and hand back a session. Skips when Postgres is down."""
    if not _postgres_available():
        pytest.skip("PostgreSQL not available")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def _tables(fresh_db):
    # For tests that use the API (its own session) but need tables to exist.
    assert inspect(engine).has_table("offers")
    yield
