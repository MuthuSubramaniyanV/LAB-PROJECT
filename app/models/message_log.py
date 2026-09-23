from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if False:  # pragma: no cover
    from app.models.customer import Customer
    from app.models.message_template import MessageTemplate
    from app.models.campaign import Campaign


class MessageLog(Base):
    __tablename__ = "message_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    campaign_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("campaigns.id", ondelete="SET NULL"), nullable=True, index=True)
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False, index=True)
    template_id: Mapped[str | None] = mapped_column(String(36), ForeignKey("message_templates.id", ondelete="SET NULL"), nullable=True, index=True)
    whatsapp_message_id: Mapped[str | None] = mapped_column(String(150), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="QUEUED", server_default=text("'QUEUED'"))
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    read_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_code: Mapped[str | None] = mapped_column(String(100), nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    campaign: Mapped["Campaign"] = relationship()
    customer: Mapped["Customer"] = relationship()
    template: Mapped["MessageTemplate"] = relationship()
