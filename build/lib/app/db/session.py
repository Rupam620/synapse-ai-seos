from __future__ import annotations

from contextlib import contextmanager


class _DummySession:
    def close(self) -> None:
        return None


@contextmanager
def SessionLocal():
    session = _DummySession()
    try:
        yield session
    finally:
        session.close()


def init_db() -> None:
    return None
