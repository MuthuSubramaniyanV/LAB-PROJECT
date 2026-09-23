from __future__ import annotations

import hashlib
from datetime import date, datetime, timedelta
from uuid import uuid4

from sqlalchemy import MetaData, Table, inspect, select, text
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.models.campaign import Campaign
from app.models.campaign_customer import CampaignCustomer
from app.models.customer import Customer
from app.models.customer_reply import CustomerReply
from app.models.customer_visit import CustomerVisit
from app.models.message_log import MessageLog
from app.models.message_template import MessageTemplate
from app.models.opt_out import OptOut
from app.models.system_setting import SystemSetting
from app.models.user import User

ADMIN_EMAIL = "admin@labdemo.local"
ADMIN_PASSWORD = "Admin@12345"
ADMIN_NAME = "Demo Admin"

TEST_TYPE_NAMES = [
    "Full Body Checkup",
    "Blood Test",
    "Diabetes Screening",
    "Thyroid Test",
    "Lipid Profile",
]

TEMPLATE_CONTENT = {
    "full_body_offer": "Hi {{customer_name}},\n\nIt's been {{inactive_days}} days since your last visit to {{lab_name}}.\n\nWe would like to invite you for a {{test_type}}.\n\nBook your appointment:\n{{booking_link}}\n\nReply STOP to opt out.",
    "dental_health_reminder": "Hi {{customer_name}},\n\nYour last visit was {{inactive_days}} days ago.\n\nA quick dental health reminder for your {{test_type}} is available.\n\nBook now: {{booking_link}}\n\nReply STOP to opt out.",
    "health_checkup_reminder": "Hi {{customer_name}},\n\nWe would like to invite you for a {{test_type}} at {{lab_name}}.\n\nYour health check is due after {{inactive_days}} days.\n\nBook your visit: {{booking_link}}\n\nReply STOP to opt out.",
}

CUSTOMER_SEEDS = [
    {"name": "Aarav Nair", "phone": "+15550000001", "location": "Mumbai", "primary_test_type": "Full Body Checkup", "days_ago": 18, "consent_whatsapp": True, "is_active": True},
    {"name": "Diya Shah", "phone": "+15550000002", "location": "Pune", "primary_test_type": "Blood Test", "days_ago": 30, "consent_whatsapp": True, "is_active": True},
    {"name": "Vihaan Rao", "phone": "+15550000003", "location": "Bengaluru", "primary_test_type": "Diabetes Screening", "days_ago": 62, "consent_whatsapp": True, "is_active": True},
    {"name": "Ananya Sen", "phone": "+15550000004", "location": "Kolkata", "primary_test_type": "Thyroid Test", "days_ago": 88, "consent_whatsapp": True, "is_active": True},
    {"name": "Rohan Mehta", "phone": "+15550000005", "location": "Delhi", "primary_test_type": "Lipid Profile", "days_ago": 95, "consent_whatsapp": True, "is_active": True},
    {"name": "Meera Iyer", "phone": "+15550000006", "location": "Chennai", "primary_test_type": "Full Body Checkup", "days_ago": 120, "consent_whatsapp": True, "is_active": True},
    {"name": "Kabir Gupta", "phone": "+15550000007", "location": "Hyderabad", "primary_test_type": "Blood Test", "days_ago": 140, "consent_whatsapp": True, "is_active": True},
    {"name": "Saanvi Joshi", "phone": "+15550000008", "location": "Ahmedabad", "primary_test_type": "Diabetes Screening", "days_ago": 180, "consent_whatsapp": True, "is_active": True},
    {"name": "Aditya Kulkarni", "phone": "+15550000009", "location": "Nashik", "primary_test_type": "Lipid Profile", "days_ago": 210, "consent_whatsapp": True, "is_active": True},
    {"name": "Naina Verma", "phone": "+15550000010", "location": "Jaipur", "primary_test_type": "Thyroid Test", "days_ago": 25, "consent_whatsapp": True, "is_active": True},
    {"name": "Ishaan Patel", "phone": "+15550000011", "location": "Surat", "primary_test_type": "Full Body Checkup", "days_ago": 55, "consent_whatsapp": True, "is_active": True},
    {"name": "Sara Khan", "phone": "+15550000012", "location": "Lucknow", "primary_test_type": "Blood Test", "days_ago": 105, "consent_whatsapp": True, "is_active": True},
    {"name": "Yuvraj Singh", "phone": "+15550000013", "location": "Pune", "primary_test_type": "Blood Test", "days_ago": 35, "consent_whatsapp": False, "is_active": True},
    {"name": "Pooja Reddy", "phone": "+15550000014", "location": "Bengaluru", "primary_test_type": "Diabetes Screening", "days_ago": 130, "consent_whatsapp": False, "is_active": True},
    {"name": "Rahul Malhotra", "phone": "+15550000015", "location": "Delhi", "primary_test_type": "Full Body Checkup", "days_ago": 170, "consent_whatsapp": True, "is_active": True},
    {"name": "Tanya Desai", "phone": "+15550000016", "location": "Mumbai", "primary_test_type": "Lipid Profile", "days_ago": 74, "consent_whatsapp": True, "is_active": True},
    {"name": "Kunal More", "phone": "+15550000017", "location": "Nagpur", "primary_test_type": "Thyroid Test", "days_ago": 50, "consent_whatsapp": True, "is_active": True},
    {"name": "Anvi Kapoor", "phone": "+15550000018", "location": "Chandigarh", "primary_test_type": "Diabetes Screening", "days_ago": 150, "consent_whatsapp": False, "is_active": True},
]

VISIT_SEEDS = [
    ("+15550000001", "Full Body Checkup", 18),
    ("+15550000001", "Blood Test", 120),
    ("+15550000002", "Blood Test", 30),
    ("+15550000002", "Thyroid Test", 190),
    ("+15550000003", "Diabetes Screening", 62),
    ("+15550000004", "Thyroid Test", 88),
    ("+15550000004", "Full Body Checkup", 220),
    ("+15550000005", "Lipid Profile", 95),
    ("+15550000006", "Full Body Checkup", 120),
    ("+15550000006", "Blood Test", 180),
    ("+15550000007", "Blood Test", 140),
    ("+15550000008", "Diabetes Screening", 180),
    ("+15550000009", "Lipid Profile", 210),
    ("+15550000010", "Thyroid Test", 25),
    ("+15550000011", "Full Body Checkup", 55),
    ("+15550000011", "Diabetes Screening", 170),
    ("+15550000012", "Blood Test", 105),
    ("+15550000013", "Blood Test", 35),
    ("+15550000014", "Diabetes Screening", 130),
    ("+15550000015", "Full Body Checkup", 170),
    ("+15550000016", "Lipid Profile", 74),
    ("+15550000017", "Thyroid Test", 50),
    ("+15550000018", "Diabetes Screening", 150),
]


def hashed_password(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def ensure_test_type_rows(db: Session) -> int:
    # The actual project schema stores test types as strings on customer/campaign rows,
    # not in a separate table. This function exists only to keep the demo metadata
    # and summary counts consistent without altering the schema.
    return len(TEST_TYPE_NAMES)


def ensure_admin_user(db: Session) -> User:
    admin = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if admin is None:
        admin = User(
            id=str(uuid4()),
            name=ADMIN_NAME,
            email=ADMIN_EMAIL,
            password_hash=hashed_password(ADMIN_PASSWORD),
            role="admin",
            is_active=True,
        )
        db.add(admin)
        db.flush()
    else:
        admin.name = ADMIN_NAME
        admin.password_hash = hashed_password(ADMIN_PASSWORD)
        admin.role = "admin"
        admin.is_active = True
    return admin


def ensure_system_setting(db: Session) -> SystemSetting:
    setting = db.query(SystemSetting).filter(SystemSetting.key == "default_inactive_days").first()
    if setting is None:
        setting = SystemSetting(id=str(uuid4()), key="default_inactive_days", value="90")
        db.add(setting)
        db.flush()
    else:
        setting.value = "90"
    return setting


def upsert_customer(db: Session, item: dict) -> Customer:
    customer = db.query(Customer).filter(Customer.phone == item["phone"]).first()
    if customer is None:
        customer = Customer(
            id=str(uuid4()),
            name=item["name"],
            phone=item["phone"],
            email=f"{item['name'].lower().replace(' ', '.')}@demo.local",
            location=item["location"],
            primary_test_type=item["primary_test_type"],
            consent_whatsapp=item["consent_whatsapp"],
            is_active=item["is_active"],
            last_visit=date.today() - timedelta(days=item["days_ago"]),
        )
        db.add(customer)
        db.flush()
    else:
        customer.name = item["name"]
        customer.email = f"{item['name'].lower().replace(' ', '.')}@demo.local"
        customer.location = item["location"]
        customer.primary_test_type = item["primary_test_type"]
        customer.consent_whatsapp = item["consent_whatsapp"]
        customer.is_active = item["is_active"]
        customer.last_visit = date.today() - timedelta(days=item["days_ago"])
    return customer


def seed_customers(db: Session) -> list[Customer]:
    customers = []
    for item in CUSTOMER_SEEDS:
        customer = upsert_customer(db, item)
        customers.append(customer)
    return customers


def seed_customer_visits(db: Session, customers: list[Customer]) -> int:
    customer_by_phone = {customer.phone: customer for customer in customers}
    inserted = 0
    for phone, test_type, days_ago in VISIT_SEEDS:
        customer = customer_by_phone.get(phone)
        if customer is None:
            continue
        visit = CustomerVisit(
            id=str(uuid4()),
            customer_id=customer.id,
            test_type=test_type,
            visit_date=date.today() - timedelta(days=days_ago),
            amount=125.00 + (inserted % 5) * 25,
            notes="Demo customer visit",
        )
        db.add(visit)
        inserted += 1
        if customer.last_visit is None or visit.visit_date > customer.last_visit:
            customer.last_visit = visit.visit_date
    return inserted


def seed_templates(db: Session) -> list[MessageTemplate]:
    templates = []
    for idx, (name, content) in enumerate(TEMPLATE_CONTENT.items(), start=1):
        existing = db.query(MessageTemplate).filter(MessageTemplate.name == name).first()
        if existing is None:
            template = MessageTemplate(
                id=str(uuid4()),
                name=name,
                language="en",
                category="MARKETING",
                template_content=content,
                meta_template_name=name,
                status="ACTIVE",
            )
            db.add(template)
            db.flush()
            templates.append(template)
        else:
            existing.language = "en"
            existing.category = "MARKETING"
            existing.template_content = content
            existing.meta_template_name = name
            existing.status = "ACTIVE"
            templates.append(existing)
    return templates


def seed_campaigns(db: Session, admin: User) -> list[Campaign]:
    specs = [
        {"name": "Full Body Checkup Re-engagement", "target_days": 90, "max_customers": 10, "location": "Mumbai", "test_type": "Full Body Checkup", "status": "APPROVED"},
        {"name": "Inactive Customer Health Reminder", "target_days": 120, "max_customers": 5, "location": "Pune", "test_type": "Blood Test", "status": "DRAFT"},
        {"name": "Long-term Customer Re-engagement", "target_days": 180, "max_customers": 8, "location": "Delhi", "test_type": "Full Body Checkup", "status": "COMPLETED"},
    ]
    campaigns = []
    for spec in specs:
        campaign = db.query(Campaign).filter(Campaign.name == spec["name"]).first()
        if campaign is None:
            campaign = Campaign(
                id=str(uuid4()),
                name=spec["name"],
                target_days=spec["target_days"],
                max_customers=spec["max_customers"],
                location=spec["location"],
                test_type=spec["test_type"],
                status=spec["status"],
                created_by=admin.id,
                description=f"Demo campaign for {spec['test_type']}",
            )
            db.add(campaign)
            db.flush()
        else:
            campaign.target_days = spec["target_days"]
            campaign.max_customers = spec["max_customers"]
            campaign.location = spec["location"]
            campaign.test_type = spec["test_type"]
            campaign.status = spec["status"]
            campaign.created_by = admin.id
        campaigns.append(campaign)
    return campaigns


def seed_campaign_customers(db: Session, campaigns: list[Campaign], customers: list[Customer]) -> int:
    inserted = 0
    statuses = ["QUEUED", "SENT", "DELIVERED", "READ", "FAILED", "REPLIED"]
    for campaign in campaigns:
        eligible = [
            customer for customer in customers
            if customer.is_active
            and customer.consent_whatsapp
            and customer.last_visit is not None
            and (date.today() - customer.last_visit).days >= campaign.target_days
            and (campaign.test_type is None or customer.primary_test_type == campaign.test_type)
            and (campaign.location is None or customer.location == campaign.location)
        ]
        eligible = sorted(eligible, key=lambda c: c.last_visit or date.min)
        for idx, customer in enumerate(eligible[: campaign.max_customers]):
            relation = db.query(CampaignCustomer).filter(CampaignCustomer.campaign_id == campaign.id, CampaignCustomer.customer_id == customer.id).first()
            if relation is None:
                relation = CampaignCustomer(
                    id=str(uuid4()),
                    campaign_id=campaign.id,
                    customer_id=customer.id,
                    segment_reason=f"Inactive for {(date.today() - customer.last_visit).days} days; consent_whatsapp=true",
                    status=statuses[idx % len(statuses)],
                )
                db.add(relation)
                inserted += 1
            else:
                relation.segment_reason = f"Inactive for {(date.today() - customer.last_visit).days} days; consent_whatsapp=true"
                relation.status = statuses[idx % len(statuses)]
    return inserted


def seed_message_logs(db: Session, campaigns: list[Campaign], templates: list[MessageTemplate], customers: list[Customer]) -> int:
    inserted = 0
    statuses = ["SENT", "DELIVERED", "READ", "FAILED"]
    customers_for_logs = customers[:12]
    for index, customer in enumerate(customers_for_logs, start=1):
        campaign = campaigns[index % len(campaigns)]
        template = templates[index % len(templates)]
        status = statuses[index % len(statuses)]
        message = MessageLog(
            id=str(uuid4()),
            campaign_id=campaign.id,
            customer_id=customer.id,
            template_id=template.id,
            whatsapp_message_id=f"demo-wa-msg-{index:03d}",
            status=status,
            sent_at=datetime.utcnow() - timedelta(days=(index + 1)),
            delivered_at=datetime.utcnow() - timedelta(days=max(1, index - 1)) if status in {"DELIVERED", "READ"} else None,
            read_at=datetime.utcnow() - timedelta(days=max(1, index - 2)) if status == "READ" else None,
            error_code="E_500" if status == "FAILED" else None,
            error_message="Demo failed delivery simulation" if status == "FAILED" else None,
        )
        db.add(message)
        inserted += 1
    return inserted


def seed_customer_replies(db: Session, customers: list[Customer]) -> int:
    replies = [
        "I would like to book an appointment.",
        "Can I come tomorrow?",
        "Please call me.",
        "Thanks, I will visit next week.",
    ]
    inserted = 0
    for idx, text in enumerate(replies):
        customer = customers[idx]
        reply = CustomerReply(
            id=str(uuid4()),
            customer_id=customer.id,
            message_text=text,
            received_at=datetime.utcnow() - timedelta(days=idx + 1),
            is_opt_out=False,
        )
        db.add(reply)
        inserted += 1
    return inserted


def seed_opt_outs(db: Session, customers: list[Customer]) -> int:
    opt_out_targets = [customers[12], customers[13], customers[17]]
    inserted = 0
    for customer in opt_out_targets:
        existing = db.query(OptOut).filter(OptOut.customer_id == customer.id).first()
        if existing is None:
            opt_out = OptOut(
                id=str(uuid4()),
                customer_id=customer.id,
                phone=customer.phone,
                reason="STOP",
                source="WHATSAPP",
            )
            db.add(opt_out)
            inserted += 1
        customer.consent_whatsapp = False
    return inserted


def validate_seed(db: Session) -> dict[str, int]:
    counts = {
        "admin": db.query(User).filter(User.email == ADMIN_EMAIL).count(),
        "customers": db.query(Customer).count(),
        "customer_visits": db.query(CustomerVisit).count(),
        "templates": db.query(MessageTemplate).count(),
        "campaigns": db.query(Campaign).count(),
        "campaign_customers": db.query(CampaignCustomer).count(),
        "message_logs": db.query(MessageLog).count(),
        "customer_replies": db.query(CustomerReply).count(),
        "opt_outs": db.query(OptOut).count(),
    }

    for campaign in db.query(Campaign).all():
        current = db.query(CampaignCustomer).filter(CampaignCustomer.campaign_id == campaign.id).count()
        if current > campaign.max_customers:
            raise ValueError(f"Campaign {campaign.name} exceeds max_customers ({current} > {campaign.max_customers})")

    opts = db.query(Customer).filter(Customer.consent_whatsapp.is_(False)).count()
    if opts < 1:
        raise ValueError("Opted-out demo customers were not created")

    return counts


def main() -> None:
    with SessionLocal() as db:
        with db.begin():
            admin = ensure_admin_user(db)
            ensure_system_setting(db)
            test_type_count = ensure_test_type_rows(db)
            customers = seed_customers(db)
            customer_visit_count = seed_customer_visits(db, customers)
            templates = seed_templates(db)
            campaigns = seed_campaigns(db, admin)
            campaign_customer_count = seed_campaign_customers(db, campaigns, customers)
            message_log_count = seed_message_logs(db, campaigns, templates, customers)
            customer_reply_count = seed_customer_replies(db, customers)
            opt_out_count = seed_opt_outs(db, customers)
            counts = validate_seed(db)

    print("========================================")
    print("DATABASE SEED COMPLETED")
    print("========================================")
    print(f"Admin: {counts['admin']}")
    print(f"Test Types: {test_type_count if test_type_count else 5}")
    print(f"Customers: {counts['customers']}")
    print(f"Customer Visits: {counts['customer_visits']}")
    print(f"Templates: {counts['templates']}")
    print(f"Campaigns: {counts['campaigns']}")
    print(f"Campaign Customers: {counts['campaign_customers']}")
    print(f"Message Logs: {counts['message_logs']}")
    print(f"Customer Replies: {counts['customer_replies']}")
    print(f"Opt-outs: {counts['opt_outs']}")
    print(f"Demo Admin Email: {ADMIN_EMAIL}")


if __name__ == "__main__":
    main()
