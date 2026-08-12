"""
Chat API Endpoints
Routes: /api/chat/message, /api/chat/sessions
"""

import uuid
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.database import crud
from backend.database.models import User
from backend.models.message import (
    MessageIn,
    ChatResponse,
    ChatSource,
    SessionCreate,
    SessionOut,
)
from backend.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/message",
    response_model=ChatResponse,
    summary="Send a chat message and receive AI agent response",
)
async def send_message(
    payload: MessageIn,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Process a user message:
    - If no session_id is provided, creates a new session.
    - Saves user message to database.
    - In Phase 2, returns a structured stub response (AI orchestration wired in Phase 5).
    - Saves assistant message to database.
    """
    session_id = payload.session_id

    # 1. Validate or create session
    if session_id:
        existing_session = await crud.get_session_by_id(db, session_id=session_id)
        if not existing_session or existing_session.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found or does not belong to current user.",
            )
    else:
        # Create new session with auto title from message snippet
        title = payload.message.strip()[:30] + ("..." if len(payload.message.strip()) > 30 else "")
        new_session = await crud.create_session(
            db,
            user_id=current_user.id,
            title=title or "New Conversation",
        )
        session_id = new_session.id

    # 2. Persist user message
    await crud.save_message(
        db,
        session_id=session_id,
        role="user",
        content=payload.message.strip(),
        agent_name=None,
        intent=None,
    )

    # 3. Generate response (Phase 2 stub; full Multi-Agent RAG wired in Phase 4 & 5)
    stub_response_text = (
        f"Thank you for contacting TechMart Electronics support! "
        f"We have received your inquiry: \"{payload.message.strip()}\". "
        f"Our support agents are here to assist you."
    )
    stub_agents = ["faq"]
    stub_intent = ["faq"]
    now = datetime.now(timezone.utc)

    # 4. Persist assistant message
    assistant_msg = await crud.save_message(
        db,
        session_id=session_id,
        role="assistant",
        content=stub_response_text,
        agent_name="faq",
        intent=stub_intent,
    )

    return ChatResponse(
        message_id=assistant_msg.id,
        response=stub_response_text,
        agents_invoked=stub_agents,
        intent=stub_intent,
        session_id=session_id,
        timestamp=now,
        sources=[],
    )


@router.get(
    "/sessions",
    response_model=List[SessionOut],
    summary="List all chat sessions for the authenticated user",
)
async def list_sessions(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve conversation session history for the current user, ordered by most recently active.
    """
    sessions = await crud.get_sessions_by_user(
        db,
        user_id=current_user.id,
        limit=limit,
        offset=offset,
    )
    return [SessionOut.model_validate(s) for s in sessions]


@router.post(
    "/sessions",
    response_model=SessionOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new chat session",
)
async def create_new_session(
    payload: Optional[SessionCreate] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Explicitly create a new conversation thread.
    """
    title = payload.title if payload and payload.title else "New Conversation"
    session = await crud.create_session(
        db,
        user_id=current_user.id,
        title=title,
    )
    return SessionOut.model_validate(session)


@router.delete(
    "/sessions/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a chat session",
)
async def delete_session_by_id(
    session_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a conversation session and its message history.
    """
    deleted = await crud.delete_session(
        db,
        session_id=session_id,
        user_id=current_user.id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or already deleted.",
        )
    return None
