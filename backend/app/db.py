import os
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "app.db")


class Base(DeclarativeBase):
    pass


DB_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DB_PATH}")

if DB_URL == "sqlite:///:memory:":
    from sqlalchemy.pool import StaticPool

    engine = create_engine(
        DB_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(DB_URL)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, _):
    dbapi_conn.execute("PRAGMA foreign_keys = ON")


@event.listens_for(engine, "checkin")
def reset_query_only(dbapi_conn, _):
    if dbapi_conn is not None:
        dbapi_conn.execute("PRAGMA query_only = OFF")


# objects stay readable after commit
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def get_session(write=False):
    session = SessionLocal()
    try:
        if not write:
            session.execute(text("PRAGMA query_only = ON"))
        yield session
        if write:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
