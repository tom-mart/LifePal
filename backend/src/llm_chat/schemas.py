from ninja import Schema
from typing import List, Dict, Optional, Any
from datetime import datetime
from uuid import UUID


class MessageSchema(Schema):
    #Schema for chat message
    role: str
    content: str


class ChatRequestSchema(Schema):
    #Schema for chat request
    message: str
    conversation_id: Optional[UUID] = None


class MessageResponseSchema(Schema):
    #Schema for individual message response
    id: UUID
    role: str
    content: str
    created_at: datetime


class IntentSchema(Schema):
    #Schema for detected intent
    intent_type: str
    confidence: float
    parameters: Dict[str, Any] = {}


class ChatResponseSchema(Schema):
    #Schema for chat response
    message: MessageResponseSchema
    conversation_id: UUID
    intent: Optional[IntentSchema] = None


class ConversationSchema(Schema):
    #Schema for conversation
    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime


class ConversationDetailSchema(ConversationSchema):
    #Schema for conversation with messages
    messages: List[MessageResponseSchema]


class ConversationListSchema(Schema):
    #Schema for list of conversations
    conversations: List[ConversationSchema]
