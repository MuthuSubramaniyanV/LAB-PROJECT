from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.database.connection import get_db
from app.models.user import User
from app.schemas.template import MessageTemplateCreate, MessageTemplateListResponse, MessageTemplateResponse, MessageTemplateUpdate
from app.services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["Templates"])


def _get_template_service(db: Session = Depends(get_db)) -> TemplateService:
    return TemplateService(db)


@router.post("", response_model=MessageTemplateResponse, status_code=status.HTTP_201_CREATED)
def create_template(
    payload: MessageTemplateCreate,
    _: User = Depends(get_current_admin),
    service: TemplateService = Depends(_get_template_service),
) -> MessageTemplateResponse:
    try:
        template = service.create_template(payload.model_dump())
        return MessageTemplateResponse.model_validate(template)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.get("", response_model=MessageTemplateListResponse)
def list_templates(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(get_current_admin),
    service: TemplateService = Depends(_get_template_service),
):
    items, total, pages = service.list_templates(page, page_size)
    return {
        "items": [MessageTemplateResponse.model_validate(item) for item in items],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages,
    }


@router.get("/{template_id}", response_model=MessageTemplateResponse)
def get_template(
    template_id: str,
    _: User = Depends(get_current_admin),
    service: TemplateService = Depends(_get_template_service),
) -> MessageTemplateResponse:
    try:
        return MessageTemplateResponse.model_validate(service.get_template(template_id))
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found") from exc


@router.put("/{template_id}", response_model=MessageTemplateResponse)
def update_template(
    template_id: str,
    payload: MessageTemplateUpdate,
    _: User = Depends(get_current_admin),
    service: TemplateService = Depends(_get_template_service),
) -> MessageTemplateResponse:
    try:
        template = service.update_template(template_id, payload.model_dump(exclude_unset=True))
        return MessageTemplateResponse.model_validate(template)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Template not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
