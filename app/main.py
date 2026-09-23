from __future__ import annotations

import hashlib
import logging
from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.database.base import Base
from app.database.connection import SessionLocal, engine
from app.models.user import User
from app.routers.admin import router as admin_router
from app.routers.auth import router as auth_router
from app.routers.campaigns import router as campaigns_router
from app.routers.customers import router as customers_router
from app.routers.messages import router as messages_router
from app.routers.templates import router as templates_router
from app.routers.webhooks import router as webhooks_router

logger = logging.getLogger("app.main")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("Application startup initiated.")
    try:
        if settings.database_url.startswith("sqlite"):
            Base.metadata.create_all(bind=engine)
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
            existing_admin = session.query(User).filter_by(email="admin@lab.local").first()
            if existing_admin is None:
                admin = User(
                    id=str(uuid4()),
                    name="System Admin",
                    email="admin@lab.local",
                    password_hash=hashlib.sha256("admin123".encode("utf-8")).hexdigest(),
                    role="admin",
                    is_active=True,
                )
                session.add(admin)
                session.commit()
            logger.info("Database connection successful.")
    except SQLAlchemyError as exc:
        logger.exception("Database connection failed during startup")
        raise RuntimeError("Database connection failed") from exc
    yield


app = FastAPI(
    title=settings.app_name,
    description="Laboratory customer re-engagement backend.",
    version="1.0.0",
    docs_url="/docs" if settings.enable_docs else None,
    redoc_url="/redoc" if settings.enable_docs else None,
    openapi_url="/openapi.json" if settings.enable_docs else None,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(admin_router, prefix=settings.api_v1_prefix)
app.include_router(customers_router, prefix=settings.api_v1_prefix)
app.include_router(campaigns_router, prefix=settings.api_v1_prefix)
app.include_router(templates_router, prefix=settings.api_v1_prefix)
app.include_router(messages_router, prefix=settings.api_v1_prefix)
app.include_router(webhooks_router, prefix=settings.api_v1_prefix)


@app.get("/health")
def health_check() -> dict[str, str]:
    try:
        with SessionLocal() as session:
            session.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except SQLAlchemyError as exc:
        logger.exception("Health check database lookup failed")
        raise RuntimeError("Database connection failed") from exc
