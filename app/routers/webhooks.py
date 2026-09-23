from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.models.customer import Customer
from app.models.customer_reply import CustomerReply
from app.models.message_log import MessageLog
from app.models.opt_out import OptOut
from app.services.whatsapp_service import OPT_OUT_KEYWORDS, WhatsAppService

router = APIRouter(prefix="/webhooks", tags=["Webhooks"])


@router.get("/whatsapp")
def verify_whatsapp_webhook(
    mode: str | None = Query(default=None),
    verify_token: str | None = Query(default=None),
    challenge: str | None = Query(default=None),
):
    service = WhatsAppService()
    response = service.build_webhook_verification_response(mode, verify_token, challenge)
    if response is None:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Verification failed")
    return response


@router.post("/whatsapp")
async def handle_whatsapp_webhook(request: Request, db: Session = Depends(get_db)) -> dict:
    try:
        payload = await request.json()
    except Exception:
        payload = {}

    if not isinstance(payload, dict):
        return {"status": "ignored"}

    service = WhatsAppService()
    for entry in payload.get("entry") or []:
        for change in entry.get("changes") or []:
            value = change.get("value") or {}
            for incoming in value.get("messages") or []:
                phone = incoming.get("from")
                customer = db.query(Customer).filter(Customer.phone == phone).first()
                if customer is None:
                    continue
                text = incoming.get("text", {}).get("body") if isinstance(incoming.get("text"), dict) else incoming.get("text") if isinstance(incoming.get("text"), str) else None
                if text is not None:
                    record = CustomerReply(
                        customer_id=customer.id,
                        message_text=text,
                        received_at=datetime.utcnow(),
                        is_opt_out=service.is_opt_out_message(text),
                    )
                    db.add(record)
                    if service.is_opt_out_message(text):
                        customer.consent_whatsapp = False
                        opt_out = OptOut(
                            customer_id=customer.id,
                            phone=customer.phone,
                            reason="STOP",
                            source="whatsapp",
                        )
                        db.add(opt_out)
                    db.commit()

            for status in value.get("statuses") or []:
                whatsapp_id = status.get("id")
                if not whatsapp_id:
                    continue
                message = db.query(MessageLog).filter(MessageLog.whatsapp_message_id == whatsapp_id).first()
                if message is None:
                    continue
                message.status = str(status.get("status") or message.status).upper()
                if message.status == "DELIVERED":
                    message.delivered_at = datetime.utcnow()
                elif message.status == "READ":
                    message.read_at = datetime.utcnow()
                elif message.status == "FAILED":
                    message.error_code = status.get("code")
                    message.error_message = status.get("message")
                db.commit()

    return {"status": "ok"}
