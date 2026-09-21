from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import Boolean, Date, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.customer_visit import CustomerVisit


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    phone: Mapped[str] = mapped_column(String(20), nullable=False, unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    date_of_birth: Mapped[date | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    location: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    last_visit: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    primary_test_type: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    consent_whatsapp: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, server_default=text("false"), index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True, server_default=text("true"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )

    visits: Mapped[list["CustomerVisit"]] = relationship(back_populates="customer", cascade="all, delete-orphan")
