from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, HttpUrl


class ActivityVariation(BaseModel):
    id: str
    name: str
    time_slot: str
    group_size_min: int
    group_size_max: int
    price_per_person: float
    currency: str = "AED"
    is_available: bool = True


class Activity(BaseModel):
    id: str
    name: str
    description: str
    images: List[HttpUrl]
    variations: List[ActivityVariation]
    cancellation_policy: str
    reschedule_policy: str


class BookingStatus(str, Enum):
    CONFIRMED = "confirmed"
    PENDING_SUPERVISOR = "pending_supervisor"
    REJECTED = "rejected"


class Booking(BaseModel):
    id: str
    activity_id: str
    variation_id: str
    customer_name: str
    customer_email: str
    group_size: int
    date: str
    status: BookingStatus
    created_at: datetime


class Escalation(BaseModel):
    id: str
    booking_id: str
    reason: str
    supervisor_email: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    supervisor_message: Optional[str] = None


class ChatRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SUPERVISOR = "supervisor"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    id: str
    conversation_id: str
    role: ChatRole
    text: str
    created_at: datetime


class ChatMessageCreate(BaseModel):
    text: str


class ChatMessageResponse(BaseModel):
    messages: List[ChatMessage]

