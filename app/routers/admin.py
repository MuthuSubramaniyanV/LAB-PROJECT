from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.database.connection import get_db
from app.models.user import User
from app.schemas.message import SettingResponse, SettingUpdateRequest
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard")
def get_dashboard(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> dict:
    return AdminService(db).get_dashboard()


@router.get("/settings")
def get_settings(admin: User = Depends(get_current_admin), db: Session = Depends(get_db)) -> dict:
    service = AdminService(db)
    return {
        "default_inactive_days": service.get_default_inactive_days(),
    }


@router.put("/settings/inactive-days", response_model=SettingResponse)
def update_inactive_days(
    payload: SettingUpdateRequest,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
) -> SettingResponse:
    service = AdminService(db)
    try:
        value = service.set_default_inactive_days(int(payload.value))
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return SettingResponse(key="default_inactive_days", value=str(value))
