from __future__ import annotations

from datetime import date, datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CustomerBase(BaseModel):
    name: Annotated[str, Field(min_length=1, max_length=100)]
    phone: Annotated[str, Field(min_length=1, max_length=20)]
    email: str | None = Field(default=None, max_length=255)
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, max_length=20)
    location: str | None = Field(default=None, max_length=100)
    last_visit: date | None = None
    primary_test_type: str | None = Field(default=None, max_length=100)
    consent_whatsapp: bool = False
    is_active: bool = True

    @field_validator("name", "phone")
    @classmethod
    def not_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("value cannot be blank")
        return cleaned

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class CustomerCreate(CustomerBase):
    pass


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    phone: str | None = Field(default=None, min_length=1, max_length=20)
    email: str | None = Field(default=None, max_length=255)
    date_of_birth: date | None = None
    gender: str | None = Field(default=None, max_length=20)
    location: str | None = Field(default=None, max_length=100)
    last_visit: date | None = None
    primary_test_type: str | None = Field(default=None, max_length=100)
    consent_whatsapp: bool | None = None
    is_active: bool | None = None

    @field_validator("name", "phone")
    @classmethod
    def not_blank(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not value.strip():
            raise ValueError("value cannot be blank")
        return value.strip()

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class CustomerResponse(CustomerBase):
    id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class CustomerVisitBase(BaseModel):
    test_type: Annotated[str, Field(min_length=1, max_length=100)]
    visit_date: date
    amount: str | float | None = None
    notes: str | None = Field(default=None, max_length=2000)

    model_config = ConfigDict(from_attributes=True, extra="forbid")

    @field_validator("test_type")
    @classmethod
    def validate_test_type(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("test_type cannot be blank")
        return value.strip()


class CustomerVisitCreate(CustomerVisitBase):
    pass


class CustomerVisitResponse(CustomerVisitBase):
    id: str
    customer_id: str
    created_at: datetime | None = None


class CustomerListResponse(BaseModel):
    items: list[CustomerResponse]
    page: int
    page_size: int
    total: int
    pages: int


class CustomerVisitListResponse(BaseModel):
    items: list[CustomerVisitResponse]
    page: int
    page_size: int
    total: int
    pages: int
