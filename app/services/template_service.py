from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.message_template import MessageTemplate

SUPPORTED_PLACEHOLDERS = {
    "customer_name",
    "lab_name",
    "inactive_days",
    "test_type",
    "discount",
    "offer_title",
    "booking_link",
}


class TemplateService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_template(self, payload: dict) -> MessageTemplate:
        content = payload.get("template_content") or ""
        self.validate_placeholders(content)
        template = MessageTemplate(**payload)
        self.db.add(template)
        self.db.commit()
        self.db.refresh(template)
        return template

    def get_template(self, template_id: str) -> MessageTemplate:
        template = self.db.get(MessageTemplate, template_id)
        if template is None:
            raise LookupError("Template not found")
        return template

    def list_templates(self, page: int, page_size: int) -> tuple[list[MessageTemplate], int, int]:
        statement = select(MessageTemplate).order_by(MessageTemplate.created_at.desc())
        total = self.db.scalar(select(func.count()).select_from(statement.subquery()))
        items = self.db.scalars(statement.offset((page - 1) * page_size).limit(page_size)).all()
        return items, total or 0, (total + page_size - 1) // page_size if total else 0

    def update_template(self, template_id: str, payload: dict) -> MessageTemplate:
        template = self.get_template(template_id)
        if payload.get("template_content") is not None:
            self.validate_placeholders(payload["template_content"])
        for key, value in payload.items():
            setattr(template, key, value)
        self.db.commit()
        self.db.refresh(template)
        return template

    @staticmethod
    def validate_placeholders(content: str) -> None:
        placeholders = set()
        for token in content.split("{{"):
            if "}}" in token:
                body = token.split("}}", 1)[0].strip()
                if body:
                    placeholders.add(body)
        unsupported = sorted(placeholders - SUPPORTED_PLACEHOLDERS)
        if unsupported:
            raise ValueError(f"Unsupported template placeholders: {', '.join(unsupported)}")
