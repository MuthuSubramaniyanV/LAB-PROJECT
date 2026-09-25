from __future__ import annotations

import hashlib
import hmac
import json
import logging
import os
from datetime import datetime
from typing import Any

import httpx

from app.core.config import settings

OPT_OUT_KEYWORDS = ("STOP", "UNSUBSCRIBE", "CANCEL", "OPT OUT")
logger = logging.getLogger("app.services.whatsapp")


class WhatsAppService:
    def __init__(self) -> None:
        self.access_token = settings.whatsapp_access_token or os.getenv("WHATSAPP_ACCESS_TOKEN")
        self.phone_number_id = settings.whatsapp_phone_number_id or os.getenv("WHATSAPP_PHONE_NUMBER_ID")
        self.business_account_id = settings.whatsapp_business_account_id or os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
        self.verify_token = settings.whatsapp_verify_token or os.getenv("WHATSAPP_VERIFY_TOKEN")
        self.app_secret = settings.whatsapp_app_secret or os.getenv("WHATSAPP_APP_SECRET")
        self.graph_api_version = settings.whatsapp_api_version or os.getenv("WHATSAPP_API_VERSION", "v18.0")

    def prepare_template_message(self, template: str, payload: dict[str, Any]) -> str:
        rendered = template
        for key, value in payload.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))
        return rendered

    @staticmethod
    def normalize_phone_number(phone: str | None) -> str | None:
        if not phone:
            return None
        cleaned = "".join(ch for ch in str(phone).strip() if ch.isdigit() or ch in "+")
        if not cleaned:
            return None
        if cleaned.startswith("00"):
            cleaned = "+" + cleaned[2:]
        if cleaned.startswith("+"):
            return cleaned
        if len(cleaned) >= 10:
            return "+" + cleaned.lstrip("0")
        return cleaned

    def is_opt_out_message(self, text: str | None) -> bool:
        if not text:
            return False
        normalized = text.strip().upper()
        return any(keyword in normalized for keyword in OPT_OUT_KEYWORDS)

    def get_base_url(self) -> str:
        return f"https://graph.facebook.com/{self.graph_api_version}"

    def build_webhook_verification_response(self, mode: str | None, token: str | None, challenge: str | None) -> str | None:
        if mode == "subscribe" and token == self.verify_token:
            return challenge
        return None

    def generate_signature(self, payload: bytes, secret: str | None = None) -> str:
        key = (secret or self.app_secret or "").encode("utf-8")
        digest = hmac.new(key, payload, hashlib.sha256).hexdigest()
        return f"sha256={digest}"

    def is_valid_signature(self, payload: bytes, header_value: str | None) -> bool:
        if not header_value:
            return settings.app_env == "test"
        expected = self.generate_signature(payload, self.app_secret)
        return hmac.compare_digest(expected, header_value.strip())

    def send_template_message(self, *, to_phone: str, template_name: str, language: str = "en_US", components: list[dict[str, Any]] | None = None, variables: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self.access_token or not self.phone_number_id:
            raise ValueError("WhatsApp configuration is missing")

        normalized = self.normalize_phone_number(to_phone)
        if not normalized:
            raise ValueError("Invalid phone number")

        body: dict[str, Any] = {
            "messaging_product": "whatsapp",
            "to": normalized,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {"code": language},
            },
        }
        if components:
            body["template"]["components"] = components
        if variables:
            parameters = [{"type": "text", "text": str(value)} for key, value in variables.items()]
            body["template"]["components"] = [{"type": "body", "parameters": parameters}]

        url = f"{self.get_base_url()}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        try:
            response = httpx.post(url, headers=headers, content=json.dumps(body), timeout=20.0)
            response.raise_for_status()
            payload = response.json()
            return payload
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text if exc.response is not None else str(exc)
            logger.exception("WhatsApp API HTTP error: %s", detail)
            raise ValueError(detail) from exc
        except httpx.TimeoutException as exc:
            logger.exception("WhatsApp API timeout")
            raise TimeoutError("WhatsApp API request timeout") from exc

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
