from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class MessageLogBase(BaseModel):
    campaign_id: str | None = None
    customer_id: str = Field(..., min_length=1)
    template_id: str | None = None
    whatsapp_message_id: str | None = Field(default=None, max_length=150)
    status: str = Field(default="QUEUED", max_length=30)
    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    read_at: datetime | None = None
    error_code: str | None = Field(default=None, max_length=100)
    error_message: str | None = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class MessageLogCreate(MessageLogBase):
    pass


class MessageLogUpdate(BaseModel):
    status: str | None = Field(default=None, max_length=30)
    whatsapp_message_id: str | None = Field(default=None, max_length=150)
    sent_at: datetime | None = None
    delivered_at: datetime | None = None
    read_at: datetime | None = None
    error_code: str | None = Field(default=None, max_length=100)
    error_message: str | None = None

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class MessageLogResponse(MessageLogBase):
    id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class MessageLogListResponse(BaseModel):
    items: list[MessageLogResponse]
    page: int
    page_size: int
    total: int
    pages: int


class CustomerReplyCreate(BaseModel):
    message_log_id: str | None = None
    customer_id: str = Field(..., min_length=1)
    message_text: str = Field(..., min_length=1)
    received_at: datetime | None = None
    is_opt_out: bool = False

    model_config = ConfigDict(from_attributes=True, extra="forbid")


class CustomerReplyResponse(CustomerReplyCreate):
    id: str
    created_at: datetime | None = None


class CustomerReplyListResponse(BaseModel):
    items: list[CustomerReplyResponse]
    page: int
    page_size: int
    total: int
    pages: int


class OptOutResponse(BaseModel):
    id: str
    customer_id: str
    phone: str
    reason: str | None = None
    source: str | None = None
    created_at: datetime | None = None


class SettingUpdateRequest(BaseModel):
    value: str = Field(..., min_length=1)

    model_config = ConfigDict(extra="forbid")


class SettingResponse(BaseModel):
    key: str
    value: str
    updated_at: datetime | None = None
