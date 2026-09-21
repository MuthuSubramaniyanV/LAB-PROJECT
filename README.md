# Laboratory Customer Re-engagement System

## 1. Project purpose
This project provides a backend for managing laboratory customers, tracking visit history, identifying inactive patients, segmenting audiences, and creating campaign target lists.

## 2. Architecture
The backend is built with FastAPI, SQLAlchemy 2.x, PostgreSQL, and Alembic. The design separates configuration, database access, domain services, and API routes so the system can expand with WhatsApp, AI, and analytics later without restructuring the core service layer.

## 3. Prerequisites
- Python 3.12+
- PostgreSQL 14+
- virtual environment support

## 4. PostgreSQL setup
Create a database and user, then grant privileges.

```bash
createdb laboratory_customer_reengagement
createdb laboratory_customer_reengagement_test
```

## 5. Virtual environment setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
```

## 6. Package installation
```bash
pip install -r requirements.txt
```

## 7. .env configuration
Copy the example file and set real values.

```bash
cp .env.example .env
```

Then edit `.env` with your local PostgreSQL connection details.

## 8. Alembic migration commands
```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
alembic downgrade -1
```

## 9. How to run the server
```bash
uvicorn app.main:app --reload
```

Production server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 10. Swagger URL
Open Swagger UI here:

```text
http://127.0.0.1:8000/docs
```

## 11. API endpoint summary
- `GET /health`
- `POST /api/v1/customers`
- `GET /api/v1/customers`
- `GET /api/v1/customers/{customer_id}`
- `GET /api/v1/customers/inactive`
- `GET /api/v1/customers/segment`
- `GET /api/v1/customers/{customer_id}/visits`
- `POST /api/v1/customers/{customer_id}/visits`
- `POST /api/v1/campaigns`
- `GET /api/v1/campaigns`
- `GET /api/v1/campaigns/{campaign_id}`
- `POST /api/v1/campaigns/{campaign_id}/populate`

## 12. How to run pytest
```bash
pytest -q
```

## 13. Example requests/responses
Create customer:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/customers \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "phone": "+15551234567",
    "email": "jane@example.com",
    "location": "Mumbai",
    "primary_test_type": "Full Body"
  }'
```

Example response:
```json
{
  "id": "...",
  "name": "Jane Doe",
  "phone": "+15551234567",
  "email": "jane@example.com",
  "location": "Mumbai",
  "primary_test_type": "Full Body",
  "consent_whatsapp": false,
  "is_active": true
}
```

## 14. Project folder structure
```text
backend/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   ├── database/
│   ├── models/
│   ├── schemas/
│   ├── repositories/
│   ├── services/
│   ├── routers/
│   └── utils/
├── alembic/
├── tests/
├── .env
├── .env.example
├── .gitignore
├── alembic.ini
├── requirements.txt
├── README.md
└── pytest.ini
```

## 15. What is intentionally NOT included yet
- React frontend
- Tailwind
- WhatsApp API integration
- Meta webhooks
- AI/Gemini features
- APScheduler, Celery, Redis
- Docker/Kubernetes deployment
- Authentication and authorization
- Analytics dashboard

## Run commands
```bash
uvicorn app.main:app --reload
pytest -q
```
