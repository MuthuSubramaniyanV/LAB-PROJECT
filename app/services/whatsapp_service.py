from __future__ import annotations

import os
from datetime import datetime
from typing import Any

from app.core.config import settings

OPT_OUT_KEYWORDS = ("STOP", "UNSUBSCRIBE", "CANCEL", "OPT OUT")


class WhatsAppService:
    def __init__(self) -> None:
        self.access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.business_account_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
        self.verify_token = os.getenv("WHATSAPP_VERIFY_TOKEN")
        self.graph_api_version = os.getenv("META_GRAPH_API_VERSION", "v18.0")

    def prepare_template_message(self, template: str, payload: dict[str, Any]) -> str:
        rendered = template
        for key, value in payload.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        return rendered

    def is_opt_out_message(self, text: str | None) -> bool:
        if not text:
            return False
        normalized = text.strip().upper()
        return any(keyword in normalized for keyword in OPT_OUT_KEYWORDS)

    def handle_webhook_status(self, payload: dict[str, Any]) -> dict[str, Any]:
        value = payload.get("value", {})
        statuses = value.get("statuses", [])
        for status in statuses:
            if status.get("id"):
                status_name = status.get("status")
                if status_name:
                    return {"whatsapp_message_id": status.get("id"), "status": str(status_name).upper()}
        return {}

    def handle_incoming_message(self, payload: dict[str, Any]) -> dict[str, Any]:
        value = payload.get("value", {})
        message = (value.get("messages") or [None])[0]
        if not message:
            return {}
        text = message.get("text", {}).get("body") if isinstance(message.get("text"), dict) else None
        if text is None and message.get("type") == "text":
            text = message.get("body")
        return {
            "customer_phone": message.get("from"),
            "message_body": text,
            "whatsapp_message_id": message.get("id"),
            "received_at": datetime.utcnow(),
        }

    def process_delivery_status(self, status: str) -> str:
        return status.upper() if status else "FAILED"

    def build_webhook_verification_response(self, mode: str | None, token: str | None, challenge: str | None) -> str | None:
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None
