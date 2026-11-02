import os
from contextlib import contextmanager

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "app.db")


class Base(DeclarativeBase):
    pass


DB_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DB_PATH}")

# journal mode delete: commit waits for running selects, "database is locked" after 5s

# in-memory db is per connection, StaticPool shares one across threads
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
    # sqlite skips fk checks unless enabled per connection
    dbapi_conn.execute("PRAGMA foreign_keys = ON")
    # pysqlite stops sending its own BEGIN, get_session sends it instead
    dbapi_conn.isolation_level = None


@event.listens_for(engine, "checkin")
def reset_query_only(dbapi_conn, _):
    # every connection goes back to the pool writable, None when invalidated
    if dbapi_conn is not None:
        dbapi_conn.execute("PRAGMA query_only = OFF")


# objects stay readable after commit
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


@contextmanager
def get_session(write=False):
    session = SessionLocal()
    try:
        if write:
            # write lock before any read, a parallel write waits here and then reads fresh data
            session.execute(text("BEGIN IMMEDIATE"))
        else:
            session.execute(text("PRAGMA query_only = ON"))
        yield session
        if write:
            session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
