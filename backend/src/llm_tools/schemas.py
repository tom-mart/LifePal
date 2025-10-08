"""
Common schemas and parameter types for tools
"""

from pydantic import BaseModel, Field
from typing import Optional, Literal, List
from datetime import datetime, date, time


class ToolResult(BaseModel):
    """Standard tool result format"""
    success: bool
    message: Optional[str] = None
    data: Optional[dict] = None
    error: Optional[str] = None


class DateTimeParams(BaseModel):
    """Common date/time parameters"""
    date: Optional[str] = Field(None, description="Date in YYYY-MM-DD format")
    time: Optional[str] = Field(None, description="Time in HH:MM format")
    datetime: Optional[str] = Field(None, description="DateTime in ISO format")


class PriorityParams(BaseModel):
    """Priority level parameters"""
    priority: Literal['low', 'medium', 'high'] = Field(
        'medium',
        description="Priority level"
    )


class PaginationParams(BaseModel):
    """Pagination parameters"""
    limit: int = Field(10, description="Number of items to return", ge=1, le=100)
    offset: int = Field(0, description="Number of items to skip", ge=0)


class FilterParams(BaseModel):
    """Common filter parameters"""
    filter_type: Optional[str] = Field(None, description="Type of filter to apply")
    search_query: Optional[str] = Field(None, description="Search query string")
    date_from: Optional[str] = Field(None, description="Start date for filtering")
    date_to: Optional[str] = Field(None, description="End date for filtering")
