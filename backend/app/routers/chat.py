from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException

from app.models.chat import ChatMessage, ChatResponse, ChatSession, SendMessageRequest
from app.services.chat_service import chat_service

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.get("/sessions", response_model=list[ChatSession])
async def list_sessions() -> list[ChatSession]:
    return await chat_service.get_sessions()


@router.post("/sessions", response_model=ChatSession, status_code=201)
async def create_session(title: Optional[str] = None) -> ChatSession:
    return await chat_service.create_session(title=title)


@router.get("/sessions/{session_id}", response_model=ChatSession)
async def get_session(session_id: str) -> ChatSession:
    session = await chat_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.delete("/sessions/{session_id}", status_code=204)
async def delete_session(session_id: str) -> None:
    deleted = await chat_service.delete_session(session_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")


@router.get("/sessions/{session_id}/messages", response_model=list[ChatMessage])
async def get_messages(session_id: str) -> list[ChatMessage]:
    session = await chat_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return await chat_service.get_messages(session_id)


@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(session_id: str, request: SendMessageRequest) -> ChatResponse:
    session = await chat_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    assistant_msg = await chat_service.send_message(session_id, request.content)
    updated_session = await chat_service.get_session(session_id)
    if not updated_session:
        raise HTTPException(status_code=500, detail="Session update failed")

    return ChatResponse(message=assistant_msg, session=updated_session)
