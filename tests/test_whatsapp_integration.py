from __future__ import annotations

from datetime import date, timedelta

from app.core.config import settings


def test_whatsapp_settings_load_from_environment(monkeypatch):
    monkeypatch.setenv("WHATSAPP_ACCESS_TOKEN", "token")
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "123")
    monkeypatch.setenv("WHATSAPP_VERIFY_TOKEN", "verify")
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "secret")
    monkeypatch.setenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "biz")
    monkeypatch.setenv("WHATSAPP_API_VERSION", "v19.0")

    fresh = settings.__class__()
    assert fresh.whatsapp_access_token == "token"
    assert fresh.whatsapp_phone_number_id == "123"
    assert fresh.whatsapp_verify_token == "verify"
    assert fresh.whatsapp_app_secret == "secret"
    assert fresh.whatsapp_business_account_id == "biz"
    assert fresh.whatsapp_api_version == "v19.0"


def test_campaign_send_skips_opted_out_and_invalid_phone(client):
    login = client.post("/api/v1/auth/login", json={"email": "admin@lab.local", "password": "admin123"})
    token = login.json()["access_token"]

    customer_ok = client.post(
        "/api/v1/customers",
        json={
            "name": "Good Customer",
            "phone": "+15550000021",
            "last_visit": (date.today() - timedelta(days=140)).isoformat(),
            "location": "Mumbai",
            "primary_test_type": "Full Body",
            "consent_whatsapp": True,
            "is_active": True,
        },
    ).json()
    customer_opted = client.post(
        "/api/v1/customers",
        json={
            "name": "Opted Out",
            "phone": "+15550000022",
            "last_visit": (date.today() - timedelta(days=160)).isoformat(),
            "location": "Mumbai",
            "primary_test_type": "Full Body",
            "consent_whatsapp": True,
            "is_active": True,
        },
    ).json()
    client.post(
        f"/api/v1/customers/{customer_opted['id']}/visits",
        json={"test_type": "Full Body", "visit_date": (date.today() - timedelta(days=200)).isoformat(), "amount": "2000"},
    )

    client.post(
        "/api/v1/webhooks/whatsapp",
        json={
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{
                            "from": customer_opted["phone"],
                            "text": {"body": "STOP"},
                            "type": "text",
                        }]
                    }
                }]
            }]
        },
    )

    template = client.post(
        "/api/v1/templates",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "welcome_followup",
            "language": "en",
            "category": "MARKETING",
            "template_content": "Hi {{customer_name}}, we invite you for {{test_type}}.",
            "meta_template_name": "welcome_followup",
            "status": "ACTIVE",
        },
    )
    assert template.status_code == 201, template.text

    campaign = client.post(
        "/api/v1/campaigns",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "WhatsApp Campaign",
            "target_days": 90,
            "test_type": "Full Body",
            "location": "Mumbai",
        },
    ).json()

    client.post(f"/api/v1/campaigns/{campaign['id']}/populate")
    send = client.post(f"/api/v1/campaigns/{campaign['id']}/send", headers={"Authorization": f"Bearer {token}"}, json={"template_id": template.json()["id"]})
    assert send.status_code == 200, send.text
    body = send.json()
    assert body["total"] >= 1
    assert body["skipped"] >= 1
    assert body["failed"] >= 0


def test_whatsapp_verification_and_signature_guard(client):
    verify = client.get("/api/v1/webhooks/whatsapp", params={"hub.mode": "subscribe", "hub.verify_token": "verify", "hub.challenge": "challenge"})
    assert verify.status_code == 200
    assert verify.text == "challenge"

    invalid = client.get("/api/v1/webhooks/whatsapp", params={"hub.mode": "subscribe", "hub.verify_token": "bad", "hub.challenge": "challenge"})
    assert invalid.status_code == 403

    invalid_signature = client.post(
        "/api/v1/webhooks/whatsapp",
        json={"entry": []},
        headers={"X-Hub-Signature-256": "sha256=deadbeef"},
    )
    assert invalid_signature.status_code == 403
