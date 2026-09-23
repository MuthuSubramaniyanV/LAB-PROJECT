from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.message_log import MessageLog

VALID_STATUSES = {"QUEUED", "SENT", "DELIVERED", "READ", "FAILED"}


class MessageService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_message(self, payload: dict) -> MessageLog:
        status = (payload.get("status") or "QUEUED").upper()
        if status not in VALID_STATUSES:
            raise ValueError("Invalid message status")
        message_payload = dict(payload)
        message_payload["status"] = status
        message = MessageLog(**message_payload)
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message

    def get_message(self, message_id: str) -> MessageLog:
        message = self.db.get(MessageLog, message_id)
        if message is None:
            raise LookupError("Message not found")
        return message

    def list_messages(self, page: int, page_size: int) -> tuple[list[MessageLog], int, int]:
        statement = select(MessageLog).order_by(MessageLog.created_at.desc())
        total = self.db.scalar(select(func.count()).select_from(statement.subquery()))
        items = self.db.scalars(statement.offset((page - 1) * page_size).limit(page_size)).all()
        return items, total or 0, (total + page_size - 1) // page_size if total else 0

    def update_status(self, message_id: str, payload: dict) -> MessageLog:
        message = self.get_message(message_id)
        status_value = (payload.get("status") or message.status).upper()
        if status_value not in VALID_STATUSES:
            raise ValueError("Invalid message status")

        message.status = status_value
        if status_value == "SENT":
            message.sent_at = message.sent_at or datetime.utcnow()
        elif status_value == "DELIVERED":
            message.delivered_at = message.delivered_at or datetime.utcnow()
        elif status_value == "READ":
            message.read_at = message.read_at or datetime.utcnow()
        elif status_value == "FAILED":
            message.error_code = payload.get("error_code") or message.error_code
            message.error_message = payload.get("error_message") or message.error_message

        if payload.get("whatsapp_message_id") is not None:
            message.whatsapp_message_id = payload["whatsapp_message_id"]

        self.db.commit()
        self.db.refresh(message)
        return message
