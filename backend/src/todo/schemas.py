from typing import List, Optional
from datetime import datetime, timedelta
from ninja import Schema, ModelSchema
from ninja.orm import create_schema
from .models import Task, Category, Tag, Reminder, TaskComment, Attachment, TaskTemplate

# Base schemas
class MessageOut(Schema):
    detail: str

# Category schemas
class CategoryIn(Schema):
    name: str
    color: str = "#808080"
    is_default: bool = False

class CategoryOut(CategoryIn):
    id: int

# Tag schemas
class TagIn(Schema):
    name: str

class TagOut(TagIn):
    id: int

# Task schemas
class TaskBase(Schema):
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: int = 2
    status: str = "todo"
    estimated_duration: Optional[int] = None
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    category_id: Optional[int] = None
    tag_ids: List[int] = []
    reward_points: int = 0
    reward_description: Optional[str] = None

class TaskCreate(TaskBase):
    assigned_to_ids: List[int] = []
    parent_task_id: Optional[int] = None
    template_id: Optional[int] = None

class TaskUpdate(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    priority: Optional[int] = None
    status: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[str] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None
    assigned_to_ids: Optional[List[int]] = None
    reward_points: Optional[int] = None
    reward_description: Optional[str] = None

class TaskOut(Schema):
    id: int
    title: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    due_date: Optional[datetime]
    completed_at: Optional[datetime]
    priority: int
    status: str
    estimated_duration: Optional[timedelta]
    actual_duration: Optional[timedelta]
    is_recurring: bool
    recurrence_rule: Optional[str]
    user_id: int
    category: Optional[CategoryOut] = None
    tags: List[TagOut] = []
    assigned_to: List[int] = []
    parent_task_id: Optional[int] = None
    template_id: Optional[int] = None
    reward_points: int
    reward_description: Optional[str]

# Comment schemas
class CommentIn(Schema):
    content: str

class CommentOut(CommentIn):
    id: int
    user_id: int
    created_at: datetime
    is_system: bool = False

# Reminder schemas
class ReminderIn(Schema):
    reminder_time: datetime
    reminder_type: str = "push"  # email, push, sms

class ReminderOut(ReminderIn):
    id: int
    task_id: int
    is_sent: bool
    created_at: datetime

# Template schemas
class TaskTemplateIn(Schema):
    name: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    estimated_duration_minutes: Optional[int] = None
    priority: int = 2

class TaskTemplateOut(TaskTemplateIn):
    id: int
    user_id: int