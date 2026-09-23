from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, UniqueConstraint, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.campaign import Campaign
    from app.models.customer import Customer


class CampaignCustomer(Base):
    __tablename__ = "campaign_customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    campaign_id: Mapped[str] = mapped_column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id"), nullable=False, index=True)
    segment_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="QUEUED", server_default=text("'QUEUED'"))
    added_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    __table_args__ = (UniqueConstraint("campaign_id", "customer_id", name="uq_campaign_customer"),)

    campaign: Mapped["Campaign"] = relationship(back_populates="campaign_customers")
    customer: Mapped["Customer"] = relationship()
