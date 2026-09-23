from __future__ import annotations

from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.campaign import Campaign
from app.models.customer import Customer
from app.models.customer_reply import CustomerReply
from app.models.message_log import MessageLog
from app.models.opt_out import OptOut
from app.models.system_setting import SystemSetting


class AdminService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_dashboard(self) -> dict:
        total_customers = self.db.scalar(select(func.count()).select_from(Customer))
        inactive_customers = self.db.scalar(
            select(func.count()).select_from(Customer).where(Customer.last_visit.is_not(None)).where(Customer.is_active.is_(True))
        )
        active_campaigns = self.db.scalar(select(func.count()).select_from(Campaign).where(Campaign.status.in_(["APPROVED", "RUNNING", "PAUSED"])))
        total_messages = self.db.scalar(select(func.count()).select_from(MessageLog))
        sent_messages = self.db.scalar(select(func.count()).select_from(MessageLog).where(MessageLog.status == "SENT"))
        delivered_messages = self.db.scalar(select(func.count()).select_from(MessageLog).where(MessageLog.status == "DELIVERED"))
        read_messages = self.db.scalar(select(func.count()).select_from(MessageLog).where(MessageLog.status == "READ"))
        failed_messages = self.db.scalar(select(func.count()).select_from(MessageLog).where(MessageLog.status == "FAILED"))
        customer_replies = self.db.scalar(select(func.count()).select_from(CustomerReply))
        opt_outs = self.db.scalar(select(func.count()).select_from(OptOut))

        return {
            "total_customers": total_customers or 0,
            "inactive_customers": inactive_customers or 0,
            "active_campaigns": active_campaigns or 0,
            "total_messages": total_messages or 0,
            "sent_messages": sent_messages or 0,
            "delivered_messages": delivered_messages or 0,
            "read_messages": read_messages or 0,
            "failed_messages": failed_messages or 0,
            "customer_replies": customer_replies or 0,
            "opt_outs": opt_outs or 0,
        }

    def get_default_inactive_days(self) -> int:
        setting = self.db.scalar(select(SystemSetting).where(SystemSetting.key == "default_inactive_days"))
        if setting is None:
            return 90
        try:
            return int(setting.value)
        except (TypeError, ValueError):
            return 90

    def set_default_inactive_days(self, days: int) -> int:
        if days <= 0:
            raise ValueError("default inactive days must be greater than zero")
        setting = self.db.scalar(select(SystemSetting).where(SystemSetting.key == "default_inactive_days"))
        if setting is None:
            setting = SystemSetting(key="default_inactive_days", value=str(days))
            self.db.add(setting)
        else:
            setting.value = str(days)
        self.db.commit()
        self.db.refresh(setting)
        return int(setting.value)
