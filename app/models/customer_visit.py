from __future__ import annotations

from datetime import date, datetime
from uuid import uuid4

from decimal import Decimal
from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class CustomerVisit(Base):
    __tablename__ = "customer_visits"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    customer_id: Mapped[str] = mapped_column(String(36), ForeignKey("customers.id", ondelete="RESTRICT"), nullable=False)
    test_type: Mapped[str] = mapped_column(String(100), nullable=False)
    visit_date: Mapped[date] = mapped_column(Date, nullable=False)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(12, 2), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))

    customer: Mapped["Customer"] = relationship(back_populates="visits")
