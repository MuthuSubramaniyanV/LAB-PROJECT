from __future__ import annotations

from datetime import date
from uuid import uuid4

from sqlalchemy.exc import IntegrityError

from app.models.customer import Customer
from app.models.customer_visit import CustomerVisit
from app.repositories.customer_repository import CustomerRepository


class CustomerService:
    def __init__(self, repository: CustomerRepository) -> None:
        self.repository = repository

    def create_customer(self, payload: dict) -> Customer:
        customer = Customer(**payload)
        try:
            return self.repository.create(customer)
        except IntegrityError as exc:
            raise ValueError("Duplicate customer phone number") from exc

    def get_customer(self, customer_id: str) -> Customer:
        customer = self.repository.get_by_id(customer_id)
        if customer is None:
            raise LookupError("Customer not found")
        return customer

    def list_customers(self, page: int, page_size: int) -> tuple[list[Customer], int, int]:
        items, total = self.repository.list(page, page_size)
        pages = (total + page_size - 1) // page_size if total else 0
        return items, total, pages

    def list_inactive_customers(
        self,
        *,
        days: int,
        consent_whatsapp: bool | None,
        location: str | None,
        test_type: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Customer], int, int]:
        items, total = self.repository.list_inactive(
            days=days,
            consent_whatsapp=consent_whatsapp,
            location=location,
            test_type=test_type,
            page=page,
            page_size=page_size,
        )
        pages = (total + page_size - 1) // page_size if total else 0
        return items, total, pages

    def segment_customers(
        self,
        *,
        days: int,
        test_type: str | None,
        location: str | None,
        consent_whatsapp: bool | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Customer], int, int]:
        items, total = self.repository.segment(
            days=days,
            test_type=test_type,
            location=location,
            consent_whatsapp=consent_whatsapp,
            page=page,
            page_size=page_size,
        )
        pages = (total + page_size - 1) // page_size if total else 0
        return items, total, pages

    def create_visit(self, customer_id: str, payload: dict) -> CustomerVisit:
        customer = self.get_customer(customer_id)
        visit = CustomerVisit(
            id=str(uuid4()),
            customer_id=customer.id,
            test_type=payload["test_type"],
            visit_date=payload["visit_date"],
            amount=payload.get("amount"),
            notes=payload.get("notes"),
        )
        if customer.last_visit is None or visit.visit_date > customer.last_visit:
            customer.last_visit = visit.visit_date
        self.repository.create_visit(visit)
        self.repository.save(customer)
        return visit

    def list_customer_visits(self, customer_id: str, page: int, page_size: int) -> tuple[list[CustomerVisit], int, int]:
        self.get_customer(customer_id)
        items, total = self.repository.list_visits(customer_id, page, page_size)
        pages = (total + page_size - 1) // page_size if total else 0
        return items, total, pages
