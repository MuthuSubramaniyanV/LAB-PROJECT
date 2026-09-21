from __future__ import annotations

from datetime import date, timedelta
from uuid import uuid4

from app.models.campaign import Campaign
from app.models.campaign_customer import CampaignCustomer
from app.repositories.campaign_repository import CampaignRepository
from app.repositories.customer_repository import CustomerRepository


class CampaignService:
    def __init__(self, campaign_repository: CampaignRepository, customer_repository: CustomerRepository) -> None:
        self.campaign_repository = campaign_repository
        self.customer_repository = customer_repository

    def create_campaign(self, payload: dict) -> Campaign:
        campaign = Campaign(**payload)
        return self.campaign_repository.create(campaign)

    def get_campaign(self, campaign_id: str) -> Campaign:
        campaign = self.campaign_repository.get_by_id(campaign_id)
        if campaign is None:
            raise LookupError("Campaign not found")
        return campaign

    def list_campaigns(self, page: int, page_size: int) -> tuple[list[Campaign], int, int]:
        items, total = self.campaign_repository.list(page, page_size)
        pages = (total + page_size - 1) // page_size if total else 0
        return items, total, pages

    def populate_campaign(self, campaign_id: str) -> dict:
        campaign = self.get_campaign(campaign_id)
        target_customers = self.campaign_repository.get_target_customers(
            target_days=campaign.target_days,
            test_type=campaign.test_type,
            location=campaign.location,
        )

        added_count = 0
        duplicates_skipped = 0
        for customer in target_customers:
            if self.campaign_repository.customer_exists(campaign.id, customer.id):
                duplicates_skipped += 1
                continue
            reason = (
                f"Inactive for {abs((date.today() - customer.last_visit).days)} days; "
                f"WhatsApp consent={str(customer.consent_whatsapp).lower()}; "
                f"test_type={customer.primary_test_type or 'Unknown'}"
            )
            relation = CampaignCustomer(
                id=str(uuid4()),
                campaign_id=campaign.id,
                customer_id=customer.id,
                segment_reason=reason,
                status="eligible",
            )
            self.campaign_repository.add_customer(relation)
            added_count += 1

        return {
            "campaign_id": campaign.id,
            "added_count": added_count,
            "duplicates_skipped": duplicates_skipped,
            "target_audience_count": len(self.campaign_repository.get_campaign_customers(campaign.id)),
        }
