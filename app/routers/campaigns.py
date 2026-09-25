from __future__ import annotations

import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.security import get_current_admin
from app.database.connection import get_db
from app.models.campaign import Campaign
from app.models.campaign_customer import CampaignCustomer
from app.models.customer import Customer
from app.models.message_log import MessageLog
from app.models.message_template import MessageTemplate
from app.models.opt_out import OptOut
from app.models.user import User
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
from app.services.whatsapp_service import WhatsAppService

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


@router.post("/{campaign_id}/send")
def send_campaign(
    campaign_id: str,
    payload: dict | None = None,
    _: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    campaign = db.get(Campaign, campaign_id)
    if campaign is None:
        raise HTTPException(status_code=404, detail="Campaign not found")

    template_id = (payload or {}).get("template_id") if isinstance(payload, dict) else None
    template = None
    if template_id:
        template = db.get(MessageTemplate, template_id)
    if template is None:
        template = db.query(MessageTemplate).filter(MessageTemplate.status == "ACTIVE").order_by(MessageTemplate.created_at.desc()).first()
    if template is None:
        raise HTTPException(status_code=404, detail="No active WhatsApp template available")

    campaign_customers = db.query(CampaignCustomer).filter(CampaignCustomer.campaign_id == campaign_id).all()
    whatsapp_service = WhatsAppService()
    sent = 0
    skipped = 0
    failed = 0
    total = len(campaign_customers)

    for relation in campaign_customers:
        customer = db.get(Customer, relation.customer_id)
        if customer is None or not customer.is_active:
            skipped += 1
            continue
        if customer.consent_whatsapp is not True:
            skipped += 1
            continue
        if db.query(OptOut).filter(OptOut.customer_id == customer.id).first() is not None:
            skipped += 1
            continue

        normalized_phone = whatsapp_service.normalize_phone_number(customer.phone)
        if not normalized_phone:
            message = MessageLog(
                campaign_id=campaign_id,
                customer_id=customer.id,
                template_id=template.id,
                status="FAILED",
                error_code="INVALID_PHONE",
                error_message="Missing or invalid customer phone number",
            )
            db.add(message)
            db.commit()
            failed += 1
            continue

        try:
            variables = {
                "customer_name": customer.name,
                "test_type": customer.primary_test_type or "your test",
                "lab_name": "Lab Flow",
                "inactive_days": str(max(1, (datetime.utcnow().date() - (customer.last_visit or datetime.utcnow().date())).days if customer.last_visit else 30)),
            }
            rendered_template = whatsapp_service.prepare_template_message(template.template_content, variables)
            body = whatsapp_service.send_template_message(
                to_phone=customer.phone,
                template_name=template.meta_template_name or template.name,
                language=template.language or "en_US",
                variables={
                    "customer_name": customer.name,
                    "test_type": customer.primary_test_type or "your test",
                },
            )
            provider_id = None
            messages = body.get("messages") if isinstance(body, dict) else []
            if isinstance(messages, list) and messages:
                provider_id = messages[0].get("id")
            message = MessageLog(
                campaign_id=campaign_id,
                customer_id=customer.id,
                template_id=template.id,
                whatsapp_message_id=provider_id,
                status="SENT",
                sent_at=datetime.utcnow(),
            )
            db.add(message)
            db.commit()
            sent += 1
        except Exception as exc:
            message = MessageLog(
                campaign_id=campaign_id,
                customer_id=customer.id,
                template_id=template.id,
                status="FAILED",
                error_code="WHATSAPP_SEND_ERROR",
                error_message=str(exc)[:500],
            )
            db.add(message)
            db.commit()
            failed += 1

    return {
        "campaign_id": campaign_id,
        "total": total,
        "sent": sent,
        "skipped": skipped,
        "failed": failed,
    }
