from ninja import Schema
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from uuid import UUID


class CheckInSchema(Schema):
    """Schema for check-in details"""
    id: UUID
    check_in_type: str
    status: str
    scheduled_time: Optional[datetime] = None
    trigger_context: Dict[str, Any] = {}
    insights: Dict[str, Any] = {}
    summary: str = ""
    actions_taken: List[Dict[str, Any]] = []
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    conversation_id: Optional[UUID] = None


class CheckInListItemSchema(Schema):
    """Schema for check-in list item"""
    id: UUID
    check_in_type: str
    status: str
    scheduled_time: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    summary: str = ""
    conversation_id: Optional[UUID] = None


class CheckInListSchema(Schema):
    """Schema for list of check-ins"""
    checkins: List[CheckInListItemSchema]


class CheckInCreateSchema(Schema):
    """Schema for creating a check-in"""
    check_in_type: str
    scheduled_time: Optional[datetime] = None
    trigger_context: Dict[str, Any] = {}


class CheckInCompleteSchema(Schema):
    """Schema for completing a check-in"""
    insights: Dict[str, Any] = {}
    summary: str = ""
    actions_taken: List[Dict[str, Any]] = []


class DailyLogCheckInSchema(Schema):
    """Simplified check-in schema for daily log"""
    id: UUID
    check_in_type: str
    status: str
    summary: str = ""
    completed_at: Optional[datetime] = None


class DailyLogSchema(Schema):
    """Schema for daily log"""
    id: UUID
    date: date
    summary: str = ""
    is_completed: bool
    checkins: List[DailyLogCheckInSchema]
