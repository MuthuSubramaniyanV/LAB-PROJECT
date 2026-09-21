from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.customer_repository import CustomerRepository
from app.schemas.campaign import (
    CampaignCreate,
    CampaignDetailResponse,
    CampaignListResponse,
    CampaignPopulateResponse,
    CampaignResponse,
    CampaignCustomerResponse,
)
from app.services.campaign_service import CampaignService

logger = logging.getLogger("app.routers.campaigns")
router = APIRouter(prefix="/campaigns", tags=["campaigns"])


def get_campaign_service(db: Session = Depends(get_db)) -> CampaignService:
    return CampaignService(CampaignRepository(db), CustomerRepository(db))


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
def create_campaign(payload: CampaignCreate, service: CampaignService = Depends(get_campaign_service)):
    try:
        campaign = service.create_campaign(payload.model_dump())
        return CampaignResponse.model_validate(campaign)
    except Exception as exc:  # pragma: no cover
        logger.exception("Campaign creation failed")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get("", response_model=CampaignListResponse)
def list_campaigns(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: CampaignService = Depends(get_campaign_service),
):
    items, total, pages = service.list_campaigns(page, page_size)
    return {
        "items": [CampaignResponse.model_validate(item) for item in items],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages,
    }


@router.get("/{campaign_id}", response_model=CampaignDetailResponse)
def get_campaign(campaign_id: str, service: CampaignService = Depends(get_campaign_service)):
    try:
        campaign = service.get_campaign(campaign_id)
        audience = service.campaign_repository.get_campaign_customers(campaign_id)
        response = CampaignResponse.model_validate(campaign).model_dump()
        response["target_audience_count"] = len(audience)
        response["target_audience"] = [
            {
                "id": item.id,
                "campaign_id": item.campaign_id,
                "customer_id": item.customer_id,
                "segment_reason": item.segment_reason,
                "status": item.status,
                "added_at": item.added_at,
            }
            for item in audience
        ]
        return response
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Campaign not found") from exc


@router.post("/{campaign_id}/populate", response_model=CampaignPopulateResponse)
def populate_campaign(campaign_id: str, service: CampaignService = Depends(get_campaign_service)):
    try:
        result = service.populate_campaign(campaign_id)
        return result
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Campaign not found") from exc
