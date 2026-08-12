"""
Pydantic schemas for Sessions, Messages, and Chat API exchanges.
"""

import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class MessageIn(BaseModel):
    """Payload sent by client to send a chat message."""
    session_id: Optional[uuid.UUID] = Field(None, description="Existing session UUID, or null to start new")
    message: str = Field(..., min_length=1, max_length=4000, description="User message content")


class MessageOut(BaseModel):
    """Message object returned from conversation history."""
    id: uuid.UUID
    session_id: uuid.UUID
    role: str  # 'user' | 'assistant'
    content: str
    agent_name: Optional[str] = None
    intent: Optional[List[str]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatSource(BaseModel):
    """Reference document cited by RAG."""
    document: str = Field(..., description="Document filename, e.g. FAQ.pdf")
    page: Optional[int] = Field(None, description="Page number within source document")


class ChatResponse(BaseModel):
    """Final unified response returned by the multi-agent system."""
    message_id: uuid.UUID
    response: str
    agents_invoked: List[str] = Field(default_factory=list)
    intent: List[str] = Field(default_factory=list)
    session_id: uuid.UUID
    timestamp: datetime
    sources: List[ChatSource] = Field(default_factory=list)


class SessionCreate(BaseModel):
    """Payload to create a new session explicitly."""
    title: Optional[str] = Field("New Conversation", max_length=255)


class SessionOut(BaseModel):
    """Session summary object."""
    id: uuid.UUID
    user_id: uuid.UUID
    title: Optional[str] = "New Conversation"
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
