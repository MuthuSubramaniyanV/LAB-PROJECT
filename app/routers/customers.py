from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.repositories.customer_repository import CustomerRepository
from app.schemas.customer import (
    CustomerCreate,
    CustomerListResponse,
    CustomerResponse,
    CustomerVisitCreate,
    CustomerVisitListResponse,
    CustomerVisitResponse,
)
from app.services.customer_service import CustomerService

logger = logging.getLogger("app.routers.customers")
router = APIRouter(prefix="/customers", tags=["customers"])


def get_customer_service(db: Session = Depends(get_db)) -> CustomerService:
    return CustomerService(CustomerRepository(db))


@router.get("/inactive")
def list_inactive_customers(
    days: int = Query(90, ge=1),
    consent_whatsapp: bool | None = None,
    location: str | None = None,
    test_type: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: CustomerService = Depends(get_customer_service),
):
    try:
        items, total, pages = service.list_inactive_customers(
            days=days,
            consent_whatsapp=consent_whatsapp,
            location=location,
            test_type=test_type,
            page=page,
            page_size=page_size,
        )
        return {
            "items": [CustomerResponse.model_validate(item).model_dump() for item in items],
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": pages,
        }
    except Exception as exc:  # pragma: no cover
        logger.exception("Failed to fetch inactive customers")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get("/segment")
def segment_customers(
    days: int = Query(90, ge=1),
    test_type: str | None = None,
    location: str | None = None,
    consent_whatsapp: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: CustomerService = Depends(get_customer_service),
):
    try:
        items, total, pages = service.segment_customers(
            days=days,
            test_type=test_type,
            location=location,
            consent_whatsapp=consent_whatsapp,
            page=page,
            page_size=page_size,
        )
        return {
            "items": [CustomerResponse.model_validate(item).model_dump() for item in items],
            "page": page,
            "page_size": page_size,
            "total": total,
            "pages": pages,
        }
    except Exception as exc:  # pragma: no cover
        logger.exception("Failed to segment customers")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.post("", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
def create_customer(payload: CustomerCreate, service: CustomerService = Depends(get_customer_service)):
    try:
        customer = service.create_customer(payload.model_dump())
        return CustomerResponse.model_validate(customer)
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover
        logger.exception("Customer creation failed")
        raise HTTPException(status_code=500, detail="Internal server error") from exc


@router.get("", response_model=CustomerListResponse)
def list_customers(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: CustomerService = Depends(get_customer_service),
):
    items, total, pages = service.list_customers(page, page_size)
    return {
        "items": [CustomerResponse.model_validate(item) for item in items],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages,
    }


@router.get("/{customer_id}", response_model=CustomerResponse)
def get_customer(customer_id: str, service: CustomerService = Depends(get_customer_service)):
    try:
        customer = service.get_customer(customer_id)
        return CustomerResponse.model_validate(customer)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Customer not found") from exc


@router.get("/{customer_id}/visits", response_model=CustomerVisitListResponse)
def list_customer_visits(
    customer_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    service: CustomerService = Depends(get_customer_service),
):
    items, total, pages = service.list_customer_visits(customer_id, page, page_size)
    return {
        "items": [CustomerVisitResponse.model_validate(item) for item in items],
        "page": page,
        "page_size": page_size,
        "total": total,
        "pages": pages,
    }


@router.post("/{customer_id}/visits", response_model=CustomerVisitResponse, status_code=status.HTTP_201_CREATED)
def create_customer_visit(
    customer_id: str,
    payload: CustomerVisitCreate,
    service: CustomerService = Depends(get_customer_service),
):
    try:
        visit = service.create_visit(customer_id, payload.model_dump())
        return CustomerVisitResponse.model_validate(visit)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Customer not found") from exc
