from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.models.customer_visit import CustomerVisit


class CustomerRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, customer: Customer) -> Customer:
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer

    def get_by_id(self, customer_id: str) -> Customer | None:
        return self.db.get(Customer, customer_id)

    def get_by_phone(self, phone: str) -> Customer | None:
        statement = select(Customer).where(Customer.phone == phone)
        return self.db.scalar(statement)

    def list(self, page: int, page_size: int) -> tuple[list[Customer], int]:
        statement = select(Customer).order_by(Customer.created_at.desc())
        total = self.db.scalar(select(func.count()).select_from(statement.subquery()))
        items = self.db.scalars(statement.offset((page - 1) * page_size).limit(page_size)).all()
        return items, total or 0

    def list_inactive(
        self,
        *,
        days: int,
        consent_whatsapp: bool | None,
        location: str | None,
        test_type: str | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Customer], int]:
        cutoff = date.today() - timedelta(days=days)
        statement = select(Customer).where(Customer.last_visit.is_not(None)).where(Customer.last_visit < cutoff)
        if consent_whatsapp is not None:
            statement = statement.where(Customer.consent_whatsapp.is_(consent_whatsapp))
        if location:
            statement = statement.where(Customer.location == location)
        if test_type:
            statement = statement.where(Customer.primary_test_type == test_type)
        statement = statement.order_by(Customer.last_visit.asc())

        total = self.db.scalar(select(func.count()).select_from(statement.subquery()))
        items = self.db.scalars(statement.offset((page - 1) * page_size).limit(page_size)).all()
        return items, total or 0

    def segment(
        self,
        *,
        days: int,
        test_type: str | None,
        location: str | None,
        consent_whatsapp: bool | None,
        page: int,
        page_size: int,
    ) -> tuple[list[Customer], int]:
        cutoff = date.today() - timedelta(days=days)
        statement = select(Customer).where(Customer.last_visit.is_not(None)).where(Customer.last_visit < cutoff)
        if test_type:
            statement = statement.where(Customer.primary_test_type == test_type)
        if location:
            statement = statement.where(Customer.location == location)
        if consent_whatsapp is not None:
            statement = statement.where(Customer.consent_whatsapp.is_(consent_whatsapp))
        statement = statement.order_by(Customer.last_visit.asc())

        total = self.db.scalar(select(func.count()).select_from(statement.subquery()))
        items = self.db.scalars(statement.offset((page - 1) * page_size).limit(page_size)).all()
        return items, total or 0

    def list_visits(self, customer_id: str, page: int, page_size: int) -> tuple[list[CustomerVisit], int]:
        statement = select(CustomerVisit).where(CustomerVisit.customer_id == customer_id).order_by(CustomerVisit.visit_date.desc())
        total = self.db.scalar(select(func.count()).select_from(statement.subquery()))
        items = self.db.scalars(statement.offset((page - 1) * page_size).limit(page_size)).all()
        return items, total or 0

    def create_visit(self, visit: CustomerVisit) -> CustomerVisit:
        self.db.add(visit)
        self.db.commit()
        self.db.refresh(visit)
        return visit

    def save(self, customer: Customer) -> Customer:
        self.db.add(customer)
        self.db.commit()
        self.db.refresh(customer)
        return customer
