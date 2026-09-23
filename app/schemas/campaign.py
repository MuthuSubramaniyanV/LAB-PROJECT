from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CampaignBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=5000)
    target_days: int = Field(default=90, gt=0)
    max_customers: int = Field(default=500, gt=0)
    test_type: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=100)
    offer_title: str | None = Field(default=None, max_length=150)
    offer_details: str | None = Field(default=None, max_length=5000)
    status: str = Field(default="DRAFT", max_length=30)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("name cannot be blank")
        return value.strip()

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class CampaignCreate(CampaignBase):
    pass


class CampaignUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = Field(default=None, max_length=5000)
    target_days: int | None = Field(default=None, gt=0)
    max_customers: int | None = Field(default=None, gt=0)
    test_type: str | None = Field(default=None, max_length=100)
    location: str | None = Field(default=None, max_length=100)
    offer_title: str | None = Field(default=None, max_length=150)
    offer_details: str | None = Field(default=None, max_length=5000)
    status: str | None = Field(default=None, max_length=30)

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class CampaignResponse(CampaignBase):
    id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CampaignDetailResponse(CampaignResponse):
    target_audience_count: int = 0
    target_audience: list["CampaignCustomerResponse"] = []


class CampaignCustomerBase(BaseModel):
    customer_id: str
    segment_reason: str | None = None
    status: str = Field(default="pending", max_length=30)

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class CampaignCustomerResponse(CampaignCustomerBase):
    id: str
    campaign_id: str
    customer_id: str
    added_at: datetime | None = None


class CampaignListResponse(BaseModel):
    items: list[CampaignResponse]
    page: int
    page_size: int
    total: int
    pages: int


class CampaignPopulateResponse(BaseModel):
    campaign_id: str
    added_count: int
    duplicates_skipped: int
    target_audience_count: int
