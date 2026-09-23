from datetime import date, timedelta


def test_admin_login_and_dashboard(client):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@lab.local", "password": "admin123"},
    )
    assert login.status_code == 200, login.text
    token = login.json()["access_token"]
    dashboard = client.get(
        "/api/v1/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert dashboard.status_code == 200, dashboard.text
    payload = dashboard.json()
    assert "total_customers" in payload
    assert "active_campaigns" in payload


def test_invalid_campaign_max_customers_is_rejected(client):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@lab.local", "password": "admin123"},
    )
    token = login.json()["access_token"]
    response = client.post(
        "/api/v1/campaigns",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Bad Campaign", "target_days": 90, "max_customers": 0},
    )
    assert response.status_code == 422


def test_template_crud_and_message_status_flow(client):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@lab.local", "password": "admin123"},
    )
    token = login.json()["access_token"]
    created = client.post(
        "/api/v1/templates",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "full_body_offer",
            "language": "en",
            "category": "MARKETING",
            "template_content": "Hi {{customer_name}}, we invite you for {{test_type}}.",
            "meta_template_name": "full_body_offer",
            "status": "ACTIVE",
        },
    )
    assert created.status_code == 201, created.text
    template_id = created.json()["id"]

    customer = client.post(
        "/api/v1/customers",
        json={
            "name": "Message Target",
            "phone": "+15550000100",
            "last_visit": (date.today() - timedelta(days=140)).isoformat(),
            "location": "Mumbai",
            "primary_test_type": "Full Body",
            "consent_whatsapp": True,
            "is_active": True,
        },
    ).json()

    message = client.post(
        "/api/v1/messages",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "campaign_id": None,
            "customer_id": customer["id"],
            "template_id": template_id,
            "status": "QUEUED",
            "whatsapp_message_id": "wamid_123",
        },
    )
    assert message.status_code == 201, message.text
    message_id = message.json()["id"]

    sent = client.patch(
        f"/api/v1/messages/{message_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "SENT"},
    )
    assert sent.status_code == 200, sent.text
    assert sent.json()["status"] == "SENT"

    delivered = client.patch(
        f"/api/v1/messages/{message_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "DELIVERED"},
    )
    assert delivered.status_code == 200

    read = client.patch(
        f"/api/v1/messages/{message_id}/status",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "READ"},
    )
    assert read.status_code == 200
    assert read.json()["status"] == "READ"


def test_stop_reply_marks_customer_opted_out(client):
    login = client.post(
        "/api/v1/auth/login",
        json={"email": "admin@lab.local", "password": "admin123"},
    )
    token = login.json()["access_token"]
    customer = client.post(
        "/api/v1/customers",
        json={
            "name": "Stop User",
            "phone": "+15550000109",
            "last_visit": (date.today() - timedelta(days=120)).isoformat(),
            "location": "Pune",
            "primary_test_type": "Blood Test",
            "consent_whatsapp": True,
            "is_active": True,
        },
    ).json()

    webhook = client.post(
        "/api/v1/webhooks/whatsapp",
        json={
            "entry": [
                {
                    "changes": [
                        {
                            "value": {
                                "messages": [
                                    {
                                        "from": customer["phone"],
                                        "text": {"body": "STOP"},
                                        "type": "text",
                                    }
                                ]
                            }
                        }
                    ]
                }
            ]
        },
    )
    assert webhook.status_code == 200

    updated = client.get(f"/api/v1/customers/{customer['id']}").json()
    assert updated["consent_whatsapp"] is False

    inactive = client.get("/api/v1/customers/inactive?days=90").json()
    assert all(item["id"] != customer["id"] for item in inactive["items"])


def test_admin_api_requires_auth(client):
    response = client.get("/api/v1/admin/dashboard")
    assert response.status_code == 401
