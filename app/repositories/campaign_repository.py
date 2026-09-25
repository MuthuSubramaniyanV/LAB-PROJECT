from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.campaign_customer import CampaignCustomer
from app.models.customer import Customer


class CampaignRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, campaign: Campaign) -> Campaign:
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def get_by_id(self, campaign_id: str) -> Campaign | None:
        return self.db.get(Campaign, campaign_id)

    def list(self, page: int, page_size: int) -> tuple[list[Campaign], int]:
        statement = select(Campaign).order_by(Campaign.created_at.desc())
        total = self.db.scalar(select(func.count()).select_from(statement.subquery()))
        items = self.db.scalars(statement.offset((page - 1) * page_size).limit(page_size)).all()
        return items, total or 0

    def get_target_customers(self, *, target_days: int, test_type: str | None, location: str | None) -> list[Customer]:
        statement = select(Customer).where(Customer.is_active.is_(True))
        if test_type:
            statement = statement.where(Customer.primary_test_type == test_type)
        if location:
            statement = statement.where(Customer.location == location)
        if target_days is not None:
            statement = statement.where(Customer.last_visit.is_not(None)).where(Customer.last_visit < __import__("datetime").date.today() - __import__("datetime").timedelta(days=target_days))
        return self.db.scalars(statement).all()

    def add_customer(self, campaign_customer: CampaignCustomer) -> CampaignCustomer:
        self.db.add(campaign_customer)
        self.db.commit()
        self.db.refresh(campaign_customer)
        return campaign_customer

    def get_campaign_customers(self, campaign_id: str) -> list[CampaignCustomer]:
        statement = select(CampaignCustomer).where(CampaignCustomer.campaign_id == campaign_id)
        return self.db.scalars(statement).all()

    def customer_exists(self, campaign_id: str, customer_id: str) -> bool:
        statement = select(CampaignCustomer.id).where(CampaignCustomer.campaign_id == campaign_id).where(CampaignCustomer.customer_id == customer_id)
        return self.db.scalar(statement) is not None
