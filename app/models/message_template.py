from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


class MessageTemplate(Base):
    __tablename__ = "message_templates"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    language: Mapped[str] = mapped_column(String(20), nullable=False, default="en")
    category: Mapped[str] = mapped_column(String(50), nullable=False, default="MARKETING")
    template_content: Mapped[str] = mapped_column(Text, nullable=False)
    meta_template_name: Mapped[str | None] = mapped_column(String(150), nullable=True)
    meta_template_id: Mapped[str | None] = mapped_column(String(150), nullable=True)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="ACTIVE", server_default=text("'ACTIVE'"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
        onupdate=text("CURRENT_TIMESTAMP"),
    )
