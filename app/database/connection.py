from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.config import settings
from app.database.base import Base

connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
poolclass = StaticPool if settings.database_url.startswith("sqlite") else None
engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=connect_args, poolclass=poolclass)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
