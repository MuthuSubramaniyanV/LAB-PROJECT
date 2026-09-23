from __future__ import annotations

import hashlib
from typing import Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.database.connection import get_db
from app.models.user import User

bearer_scheme = HTTPBearer(auto_error=False)


def _token_secret() -> str:
    return settings.jwt_secret or "lab-local-secret"


def create_access_token(user: User) -> str:
    digest = hashlib.sha256(f"{user.id}:{_token_secret()}".encode("utf-8")).hexdigest()
    return f"{user.id}.{digest}"


def verify_access_token(token: str) -> str:
    if not token or "." not in token:
        raise ValueError("Invalid token")
    user_id, digest = token.split(".", 1)
    expected = hashlib.sha256(f"{user_id}:{_token_secret()}".encode("utf-8")).hexdigest()
    if digest != expected:
        raise ValueError("Invalid token")
    return user_id


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> User:
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required")

    try:
        user_id = verify_access_token(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials") from exc

    user = db.get(User, user_id)
    if user is None or user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return user
