from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta


@dataclass
class SegmentationCriteria:
    days: int = 90
    test_type: str | None = None
    location: str | None = None
    consent_whatsapp: bool | None = None


class SegmentationService:
    def build_inactive_filter(self, criteria: SegmentationCriteria) -> dict:
        return {
            "days": criteria.days,
            "test_type": criteria.test_type,
            "location": criteria.location,
            "consent_whatsapp": criteria.consent_whatsapp,
        }
