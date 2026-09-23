from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.database.connection import get_db
from app.models.user import User
from app.schemas.message import MessageLogCreate, MessageLogListResponse, MessageLogResponse, MessageLogUpdate
from app.services.message_service import MessageService

router = APIRouter(prefix="/messages", tags=["Messages"])


def _get_message_service(db: Session = Depends(get_db)) -> MessageService:
    return MessageService(db)


@router.post("", response_model=MessageLogResponse, status_code=status.HTTP_201_CREATED)
def create_message(
    payload: MessageLogCreate,
    _: User = Depends(get_current_admin),
    service: MessageService = Depends(_get_message_service),
) -> MessageLogResponse:
    try:
        message = service.create_message(payload.model_dump())
        return MessageLogResponse.model_validate(message)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("", response_model=MessageLogListResponse)
def list_messages(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(get_current_admin),
    service: MessageService = Depends(_get_message_service),
):
    items, total, pages = service.list_messages(page, page_size)
    return {
        "items": [MessageLogResponse.model_validate(item) for item in items],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages,
    }


@router.get("/{message_id}", response_model=MessageLogResponse)
def get_message(
    message_id: str,
    _: User = Depends(get_current_admin),
    service: MessageService = Depends(_get_message_service),
) -> MessageLogResponse:
    try:
        return MessageLogResponse.model_validate(service.get_message(message_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found") from exc


@router.patch("/{message_id}/status", response_model=MessageLogResponse)
def update_message_status(
    message_id: str,
    payload: MessageLogUpdate,
    _: User = Depends(get_current_admin),
    service: MessageService = Depends(_get_message_service),
) -> MessageLogResponse:
    try:
        return MessageLogResponse.model_validate(service.update_status(message_id, payload.model_dump(exclude_unset=True)))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
