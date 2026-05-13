from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ChatMessage(BaseModel):
    id: Optional[str] = None
    session_id: str
    role: MessageRole
    content: str
    timestamp: Optional[str] = None


class ChatSession(BaseModel):
    id: str
    title: str = "New Chat"
    created_at: str
    updated_at: str
    message_count: int = 0


class CreateSessionRequest(BaseModel):
    title: Optional[str] = Field(default=None, description="Session title")


class SendMessageRequest(BaseModel):
    content: str = Field(..., description="User message content")


class ChatResponse(BaseModel):
    message: ChatMessage
    session: ChatSession
