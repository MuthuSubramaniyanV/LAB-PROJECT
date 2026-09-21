from datetime import date, timedelta


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_customer(client):
    payload = {
        "name": "Jane Doe",
        "phone": "+15550000001",
        "email": "jane@example.com",
        "location": "Mumbai",
        "primary_test_type": "Full Body",
        "consent_whatsapp": True,
    }
    response = client.post("/api/v1/customers", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert data["phone"] == payload["phone"]
    assert data["location"] == payload["location"]


def test_list_customers(client):
    client.post("/api/v1/customers", json={"name": "A", "phone": "+15550000002"})
    client.post("/api/v1/customers", json={"name": "B", "phone": "+15550000003"})
    response = client.get("/api/v1/customers?page=1&page_size=10")
    assert response.status_code == 200
    payload = response.json()
    assert payload["page"] == 1
    assert payload["page_size"] == 10
    assert payload["items"]


def test_retrieve_customer(client):
    created = client.post("/api/v1/customers", json={"name": "Retrieve Me", "phone": "+15550000004"}).json()
    response = client.get(f"/api/v1/customers/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_duplicate_phone_returns_409(client):
    payload = {"name": "Dup Person", "phone": "+15550000005"}
    client.post("/api/v1/customers", json=payload)
    response = client.post("/api/v1/customers", json=payload)
    assert response.status_code == 409


def test_inactive_customers_over_90_days(client):
    client.post(
        "/api/v1/customers",
        json={"name": "Inactive One", "phone": "+15550000006", "last_visit": (date.today() - timedelta(days=120)).isoformat()},
    )
    response = client.get("/api/v1/customers/inactive?days=90")
    assert response.status_code == 200
    items = response.json()["items"]
    assert any(item["phone"] == "+15550000006" for item in items)


def test_consent_filtering(client):
    client.post("/api/v1/customers", json={"name": "Consent 1", "phone": "+15550000007", "consent_whatsapp": True})
    client.post("/api/v1/customers", json={"name": "Consent 2", "phone": "+15550000008", "consent_whatsapp": False})
    response = client.get("/api/v1/customers/inactive?days=365&consent_whatsapp=true")
    assert response.status_code == 200
    items = response.json()["items"]
    assert all(item["consent_whatsapp"] is True for item in items)


def test_test_type_segmentation(client):
    client.post("/api/v1/customers", json={"name": "Segment Type", "phone": "+15550000009", "primary_test_type": "Full Body", "last_visit": (date.today() - timedelta(days=200)).isoformat()})
    response = client.get("/api/v1/customers/segment?days=90&test_type=Full Body")
    assert response.status_code == 200
    items = response.json()["items"]
    assert any(item["phone"] == "+15550000009" for item in items)


def test_location_segmentation(client):
    client.post("/api/v1/customers", json={"name": "Location User", "phone": "+15550000010", "location": "Pune", "last_visit": (date.today() - timedelta(days=180)).isoformat()})
    response = client.get("/api/v1/customers/segment?days=90&location=Pune")
    assert response.status_code == 200
    items = response.json()["items"]
    assert any(item["phone"] == "+15550000010" for item in items)


def test_create_visit_and_update_last_visit(client):
    customer = client.post("/api/v1/customers", json={"name": "Visit Person", "phone": "+15550000011"}).json()
    response = client.post(
        f"/api/v1/customers/{customer['id']}/visits",
        json={"test_type": "Full Body", "visit_date": (date.today() - timedelta(days=10)).isoformat(), "amount": "2500.00", "notes": "Follow-up"},
    )
    assert response.status_code == 201
    customer_after = client.get(f"/api/v1/customers/{customer['id']}").json()
    assert customer_after["last_visit"] == (date.today() - timedelta(days=10)).isoformat()


def test_customer_visits_list(client):
    customer = client.post("/api/v1/customers", json={"name": "Visits List", "phone": "+15550000012"}).json()
    client.post(
        f"/api/v1/customers/{customer['id']}/visits",
        json={"test_type": "Blood Test", "visit_date": date.today().isoformat(), "amount": "800.00"},
    )
    response = client.get(f"/api/v1/customers/{customer['id']}/visits")
    assert response.status_code == 200
    items = response.json()["items"]
    assert items[0]["test_type"] == "Blood Test"
