from app.db import Base, engine


# every migration is idempotent and runs on every startup
def apply_migrations():
    _migration_000_create_db()


def _migration_000_create_db():
    # idempotent: no op if tables already exist
    Base.metadata.create_all(engine)
