"""initial schema

Revision ID: 202609230001
Revises: 
Create Date: 2026-09-23 00:00:00.000000

"""
from __future__ import annotations

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "202609230001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=30), server_default=sa.text("'admin'"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)

    op.create_table(
        "customers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("gender", sa.String(length=20), nullable=True),
        sa.Column("location", sa.String(length=100), nullable=True),
        sa.Column("last_visit", sa.Date(), nullable=True),
        sa.Column("primary_test_type", sa.String(length=100), nullable=True),
        sa.Column("consent_whatsapp", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_customers_phone"), "customers", ["phone"], unique=True)
    op.create_index(op.f("ix_customers_location"), "customers", ["location"], unique=False)
    op.create_index(op.f("ix_customers_last_visit"), "customers", ["last_visit"], unique=False)
    op.create_index(op.f("ix_customers_primary_test_type"), "customers", ["primary_test_type"], unique=False)
    op.create_index(op.f("ix_customers_consent_whatsapp"), "customers", ["consent_whatsapp"], unique=False)

    op.create_table(
        "customer_visits",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("test_type", sa.String(length=100), nullable=False),
        sa.Column("visit_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "campaigns",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("target_days", sa.Integer(), server_default=sa.text("90"), nullable=False),
        sa.Column("max_customers", sa.Integer(), server_default=sa.text("500"), nullable=False),
        sa.Column("test_type", sa.String(length=100), nullable=True),
        sa.Column("location", sa.String(length=100), nullable=True),
        sa.Column("offer_title", sa.String(length=150), nullable=True),
        sa.Column("offer_details", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), server_default=sa.text("'DRAFT'"), nullable=False),
        sa.Column("created_by", sa.String(length=36), nullable=True),
        sa.Column("approved_by", sa.String(length=36), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_campaigns_created_by"), "campaigns", ["created_by"], unique=False)
    op.create_index(op.f("ix_campaigns_approved_by"), "campaigns", ["approved_by"], unique=False)

    op.create_table(
        "campaign_customers",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("campaign_id", sa.String(length=36), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("segment_reason", sa.Text(), nullable=True),
        sa.Column("status", sa.String(length=30), server_default=sa.text("'QUEUED'"), nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"]),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("campaign_id", "customer_id", name="uq_campaign_customer"),
    )
    op.create_index(op.f("ix_campaign_customers_campaign_id"), "campaign_customers", ["campaign_id"], unique=False)
    op.create_index(op.f("ix_campaign_customers_customer_id"), "campaign_customers", ["customer_id"], unique=False)

    op.create_table(
        "message_templates",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("name", sa.String(length=150), nullable=False),
        sa.Column("language", sa.String(length=20), server_default="en", nullable=False),
        sa.Column("category", sa.String(length=50), server_default="MARKETING", nullable=False),
        sa.Column("template_content", sa.Text(), nullable=False),
        sa.Column("meta_template_name", sa.String(length=150), nullable=True),
        sa.Column("meta_template_id", sa.String(length=150), nullable=True),
        sa.Column("status", sa.String(length=30), server_default=sa.text("'ACTIVE'"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "message_logs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("campaign_id", sa.String(length=36), nullable=True),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("template_id", sa.String(length=36), nullable=True),
        sa.Column("whatsapp_message_id", sa.String(length=150), nullable=True),
        sa.Column("status", sa.String(length=30), server_default=sa.text("'QUEUED'"), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("delivered_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_code", sa.String(length=100), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["campaign_id"], ["campaigns.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["template_id"], ["message_templates.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_message_logs_campaign_id"), "message_logs", ["campaign_id"], unique=False)
    op.create_index(op.f("ix_message_logs_customer_id"), "message_logs", ["customer_id"], unique=False)
    op.create_index(op.f("ix_message_logs_template_id"), "message_logs", ["template_id"], unique=False)
    op.create_index(op.f("ix_message_logs_whatsapp_message_id"), "message_logs", ["whatsapp_message_id"], unique=False)

    op.create_table(
        "customer_replies",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("message_log_id", sa.String(length=36), nullable=True),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("message_text", sa.Text(), nullable=False),
        sa.Column("received_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("is_opt_out", sa.Boolean(), server_default=sa.text("false"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["message_log_id"], ["message_logs.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_customer_replies_message_log_id"), "customer_replies", ["message_log_id"], unique=False)
    op.create_index(op.f("ix_customer_replies_customer_id"), "customer_replies", ["customer_id"], unique=False)

    op.create_table(
        "opt_outs",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("customer_id", sa.String(length=36), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("reason", sa.String(length=200), nullable=True),
        sa.Column("source", sa.String(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_opt_outs_customer_id"), "opt_outs", ["customer_id"], unique=False)
    op.create_index(op.f("ix_opt_outs_phone"), "opt_outs", ["phone"], unique=False)

    op.create_table(
        "system_settings",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("CURRENT_TIMESTAMP"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_system_settings_key"), "system_settings", ["key"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_system_settings_key"), table_name="system_settings")
    op.drop_table("system_settings")
    op.drop_index(op.f("ix_opt_outs_phone"), table_name="opt_outs")
    op.drop_index(op.f("ix_opt_outs_customer_id"), table_name="opt_outs")
    op.drop_table("opt_outs")
    op.drop_index(op.f("ix_customer_replies_customer_id"), table_name="customer_replies")
    op.drop_index(op.f("ix_customer_replies_message_log_id"), table_name="customer_replies")
    op.drop_table("customer_replies")
    op.drop_index(op.f("ix_message_logs_whatsapp_message_id"), table_name="message_logs")
    op.drop_index(op.f("ix_message_logs_template_id"), table_name="message_logs")
    op.drop_index(op.f("ix_message_logs_customer_id"), table_name="message_logs")
    op.drop_index(op.f("ix_message_logs_campaign_id"), table_name="message_logs")
    op.drop_table("message_logs")
    op.drop_table("message_templates")
    op.drop_index(op.f("ix_campaign_customers_customer_id"), table_name="campaign_customers")
    op.drop_index(op.f("ix_campaign_customers_campaign_id"), table_name="campaign_customers")
    op.drop_table("campaign_customers")
    op.drop_index(op.f("ix_campaigns_approved_by"), table_name="campaigns")
    op.drop_index(op.f("ix_campaigns_created_by"), table_name="campaigns")
    op.drop_table("campaigns")
    op.drop_table("customer_visits")
    op.drop_index(op.f("ix_customers_consent_whatsapp"), table_name="customers")
    op.drop_index(op.f("ix_customers_primary_test_type"), table_name="customers")
    op.drop_index(op.f("ix_customers_last_visit"), table_name="customers")
    op.drop_index(op.f("ix_customers_location"), table_name="customers")
    op.drop_index(op.f("ix_customers_phone"), table_name="customers")
    op.drop_table("customers")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
