from ninja import Schema
from typing import Optional
from uuid import UUID
from datetime import datetime


class PushSubscriptionSchema(Schema):
    """Schema for creating a push subscription"""
    endpoint: str
    keys: dict  # Contains p256dh and auth keys
    user_agent: Optional[str] = None


class PushSubscriptionResponseSchema(Schema):
    """Schema for push subscription response"""
    id: UUID
    endpoint: str
    created_at: datetime
    is_active: bool


class SendPushNotificationSchema(Schema):
    """Schema for sending a push notification"""
    title: str
    body: str
    icon: Optional[str] = None
    url: Optional[str] = None
    tag: Optional[str] = None
    requireInteraction: Optional[bool] = False


class VAPIDPublicKeySchema(Schema):
    """Schema for VAPID public key"""
    public_key: str


class TestNotificationSchema(Schema):
    """Schema for test notification"""
    message: Optional[str] = "This is a test notification from LifePal!"
