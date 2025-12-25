"""Schemas for chat API"""
from typing import Optional
from ninja import Schema
from pydantic import BaseModel


class ChatRequest(Schema):
    message: str
    agent_id: Optional[int] = None  # Optional: Defaults to Operator if not provided
    conversation_id: Optional[int] = None


class ChatResponse(Schema):
    conversation_id: int
    agent_id: int
    agent_name: str
    message: str
    reasoning: Optional[str] = None


class AgentSchema(BaseModel):
    id: int
    name: str
    model_name: str
    system_prompt: str
    
    class Config:
        from_attributes = True
