from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

_engine_kwargs = {}
if settings.database_url.startswith("sqlite"):
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(settings.database_url, **_engine_kwargs)

# Session-Factory – wird per Depends(get_db) in die Routes injiziert
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

# Basisklasse für alle Domain-Entities (User, Message, Quiz, ...)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
