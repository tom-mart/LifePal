from ninja import Schema
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import EmailStr, Field, validator

# Working Registration Schema
class UserRegistrationSchema(Schema):
    username: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None

# Working Login Schema
class LoginSchema(Schema):
    username: EmailStr
    password: str

class UserProfileSchema(Schema):
    id: UUID
    preferred_name: Optional[str] = None
    bio: Optional[str] = None

class UserProfileUpdateSchema(Schema):
    preferred_name: Optional[str] = None
    bio: Optional[str] = None

class UserSettingsSchema(Schema):
    id: UUID
    timezone: str
    theme: str
    email_notifications: bool
    push_notifications: bool
    allow_relationship_requests: bool
    data_sharing_consent: bool
    last_active: Optional[datetime] = None
    login_count: int

class UserSettingsUpdateSchema(Schema):
    timezone: Optional[str] = None
    theme: Optional[str] = None
    email_notifications: Optional[bool] = None
    push_notifications: Optional[bool] = None
    allow_relationship_requests: Optional[bool] = None
    data_sharing_consent: Optional[bool] = None

# Personal Information
class PersonalInfoSchema(Schema):
    age: Optional[int] = None
    gender: Optional[str] = None
    ethnic_background: Optional[str] = None
    occupation: Optional[str] = None
    relationship_status: Optional[str] = None
    living_situation: Optional[str] = None
    has_children: Optional[bool] = None
    children_info: Optional[str] = None

    @staticmethod
    def validate_age(value: int) -> int:
        if value and (value < 0 or value > 120):
            raise ValueError("Age must be between 0 and 120")
        return value

# Wellbeing Context
class WellbeingContextSchema(Schema):
    health_conditions: Optional[str] = None
    mental_health_history: Optional[str] = None
    current_challenges: Optional[str] = None
    stress_factors: Optional[str] = None
    coping_mechanisms: Optional[str] = None

# Preferences
class PreferencesSchema(Schema):
    communication_style: Optional[str] = None
    learning_style: Optional[str] = None
    response_preferences: Optional[str] = None

# Goals and Values
class GoalsValuesSchema(Schema):
    personal_goals: Optional[str] = None
    professional_goals: Optional[str] = None
    core_values: Optional[str] = None
    interests: Optional[str] = None

# Daily Routine
class DailyRoutineSchema(Schema):
    typical_schedule: Optional[str] = None
    sleep_pattern: Optional[str] = None

# Support System
class SupportSystemSchema(Schema):
    support_network: Optional[str] = None
    professional_support: Optional[str] = None

# LifePal Preferences
class LifePalPreferencesSchema(Schema):
    lifepal_usage_goals: Optional[str] = None
    topics_of_interest: Optional[str] = None
    topics_to_avoid: Optional[str] = None

# Main LLM Context Schemas
class LLMContextProfileSchema(Schema):
    """Schema for reading complete LLM context profile"""
    id: UUID
    user_id: int
    age: Optional[int] = None
    gender: Optional[str] = None
    ethnic_background: Optional[str] = None
    occupation: Optional[str] = None
    relationship_status: Optional[str] = None
    living_situation: Optional[str] = None
    has_children: Optional[bool] = None
    children_info: Optional[str] = None
    health_conditions: Optional[str] = None
    mental_health_history: Optional[str] = None
    current_challenges: Optional[str] = None
    stress_factors: Optional[str] = None
    coping_mechanisms: Optional[str] = None
    communication_style: Optional[str] = None
    learning_style: Optional[str] = None
    response_preferences: Optional[str] = None
    personal_goals: Optional[str] = None
    professional_goals: Optional[str] = None
    core_values: Optional[str] = None
    interests: Optional[str] = None
    typical_schedule: Optional[str] = None
    sleep_pattern: Optional[str] = None
    support_network: Optional[str] = None
    professional_support: Optional[str] = None
    lifepal_usage_goals: Optional[str] = None
    topics_of_interest: Optional[str] = None
    topics_to_avoid: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "user_id": 1,
                "age": 30,
                "gender": "M"
            }
        }

# Create Schema - All fields optional except user
class LLMContextProfileCreateSchema(Schema):
    """Schema for creating a profile"""
    age: Optional[int] = None
    gender: Optional[str] = None
    ethnic_background: Optional[str] = None
    occupation: Optional[str] = None
    relationship_status: Optional[str] = None
    living_situation: Optional[str] = None
    has_children: Optional[bool] = None
    children_info: Optional[str] = None
    health_conditions: Optional[str] = None
    mental_health_history: Optional[str] = None
    current_challenges: Optional[str] = None
    stress_factors: Optional[str] = None
    coping_mechanisms: Optional[str] = None
    communication_style: Optional[str] = None
    learning_style: Optional[str] = None
    response_preferences: Optional[str] = None
    personal_goals: Optional[str] = None
    professional_goals: Optional[str] = None
    core_values: Optional[str] = None
    interests: Optional[str] = None
    typical_schedule: Optional[str] = None
    sleep_pattern: Optional[str] = None
    support_network: Optional[str] = None
    professional_support: Optional[str] = None
    lifepal_usage_goals: Optional[str] = None
    topics_of_interest: Optional[str] = None
    topics_to_avoid: Optional[str] = None

    @staticmethod
    def validate_age(value: int) -> int:
        if value is not None and (value < 0 or value > 120):
            raise ValueError("Age must be between 0 and 120")
        return value
        
# Update Schemas - Only include fields that can be updated
class LLMContextProfileUpdateSchema(Schema):
    """Schema for updating LLM context profile"""
    personal_info: Optional[PersonalInfoSchema] = None
    wellbeing: Optional[WellbeingContextSchema] = None
    preferences: Optional[PreferencesSchema] = None
    goals_values: Optional[GoalsValuesSchema] = None
    daily_routine: Optional[DailyRoutineSchema] = None
    support_system: Optional[SupportSystemSchema] = None
    lifepal_preferences: Optional[LifePalPreferencesSchema] = None

# List View Schema
class LLMContextProfileListSchema(Schema):
    """Schema for list view of LLM context profiles"""
    user_id: int
    age: Optional[int] = None
    occupation: Optional[str] = None
    communication_style: Optional[str] = None
    last_updated: datetime