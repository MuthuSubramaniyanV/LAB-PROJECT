import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent
os.chdir(backend_dir)

os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["TEST_DATABASE_URL"] = "sqlite://"
os.environ["API_V1_PREFIX"] = "/api/v1"
os.environ["ENABLE_DOCS"] = "true"
os.environ["CORS_ORIGINS"] = "http://localhost:3000"

from app.database.base import Base
from app.database.connection import engine
from app.main import app


def reset_database() -> None:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture(scope="function")
def client() -> TestClient:
    reset_database()
    return TestClient(app)
