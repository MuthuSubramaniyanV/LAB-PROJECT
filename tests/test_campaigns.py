from datetime import date, timedelta


def test_create_campaign(client):
    payload = {
        "name": "Spring Re-engagement",
        "description": "Bring them back for wellness checkups.",
        "target_days": 90,
        "test_type": "Full Body",
        "location": "Mumbai",
        "offer_title": "Free consultation",
        "offer_details": "Get a complimentary assessment.",
        "status": "draft",
    }
    response = client.post("/api/v1/campaigns", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["target_days"] == 90


def test_populate_campaign(client):
    customer = client.post(
        "/api/v1/customers",
        json={
            "name": "Campaign Target",
            "phone": "+15550000013",
            "last_visit": (date.today() - timedelta(days=140)).isoformat(),
            "location": "Mumbai",
            "primary_test_type": "Full Body",
            "consent_whatsapp": True,
            "is_active": True,
        },
    ).json()
    campaign = client.post(
        "/api/v1/campaigns",
        json={
            "name": "Campaign Targeting",
            "target_days": 90,
            "test_type": "Full Body",
            "location": "Mumbai",
        },
    ).json()

    response = client.post(f"/api/v1/campaigns/{campaign['id']}/populate")
    assert response.status_code == 200
    body = response.json()
    assert body["added_count"] >= 1

    campaign_detail = client.get(f"/api/v1/campaigns/{campaign['id']}").json()
    assert campaign_detail["target_audience_count"] >= 1
    assert customer["id"] in [item["customer_id"] for item in campaign_detail["target_audience"]]


def test_duplicate_campaign_customer_is_prevented(client):
    client.post(
        "/api/v1/customers",
        json={
            "name": "No Duplicate",
            "phone": "+15550000014",
            "last_visit": (date.today() - timedelta(days=160)).isoformat(),
            "location": "Pune",
            "primary_test_type": "Blood Test",
            "consent_whatsapp": True,
            "is_active": True,
        },
    )
    campaign = client.post("/api/v1/campaigns", json={"name": "Duplicate Check", "target_days": 90, "location": "Pune", "test_type": "Blood Test"}).json()
    first = client.post(f"/api/v1/campaigns/{campaign['id']}/populate")
    second = client.post(f"/api/v1/campaigns/{campaign['id']}/populate")
    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["added_count"] == 0
