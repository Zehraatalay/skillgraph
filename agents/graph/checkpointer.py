from contextlib import contextmanager
from pathlib import Path

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver


def create_checkpointer():
    """Create an in-memory checkpointer for tests."""
    return InMemorySaver()


@contextmanager
def create_sqlite_checkpointer(db_path: str | Path):
    """Create a persistent SQLite checkpointer."""
    db_path = Path(db_path)

    db_path.parent.mkdir(parents=True, exist_ok=True)

    with SqliteSaver.from_conn_string(str(db_path)) as checkpointer:
        yield checkpointer