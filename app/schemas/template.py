from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MessageTemplateBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=150)
    language: str = Field(default="en", min_length=1, max_length=20)
    category: str = Field(default="MARKETING", min_length=1, max_length=50)
    template_content: str = Field(..., min_length=1)
    meta_template_name: str | None = Field(default=None, max_length=150)
    meta_template_id: str | None = Field(default=None, max_length=150)
    status: str = Field(default="ACTIVE", max_length=30)

    @field_validator("name", "language", "category")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("value cannot be blank")
        return value

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class MessageTemplateCreate(MessageTemplateBase):
    pass


class MessageTemplateUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    language: str | None = Field(default=None, min_length=1, max_length=20)
    category: str | None = Field(default=None, min_length=1, max_length=50)
    template_content: str | None = Field(default=None, min_length=1)
    meta_template_name: str | None = Field(default=None, max_length=150)
    meta_template_id: str | None = Field(default=None, max_length=150)
    status: str | None = Field(default=None, max_length=30)

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class MessageTemplateResponse(MessageTemplateBase):
    id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MessageTemplateListResponse(BaseModel):
    items: list[MessageTemplateResponse]
    page: int
    page_size: int
    total: int
    pages: int
