"""
Chat API Endpoints
Routes: /api/chat/message, /api/chat/sessions
Wired with Multi-Agent AI Orchestration (Intent Detector -> Agent Router -> RAG Agents -> Aggregator).
"""

import uuid
import time
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
from backend.agents.intent_detector import get_intent_detector
from backend.agents.router import get_agent_router
from backend.agents.aggregator import get_response_aggregator
from backend.utils.logger import get_logger

logger = get_logger("chat_api")
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
    Process a customer support message through the Multi-Agent AI Orchestration pipeline:
    1. Validates or creates a conversation session.
    2. Persists the incoming user message in the database.
    3. Fetches recent conversation history for contextual grounding.
    4. Classifies intent(s) via the Intent Detection Agent.
    5. Routes to responsible domain agent(s) (Billing, Technical, Product, Complaint, FAQ).
    6. Concurrently executes agents with scoped RAG retrieval & LLM generation.
    7. Synthesizes a unified response via the Response Aggregator.
    8. Persists the AI response and source citations to the database.
    9. Returns the complete ChatResponse payload.
    """
    pipeline_start = time.time()
    session_id = payload.session_id
    user_query = payload.message.strip()

    # 1. Validate or create session
    existing_session = None
    if session_id:
        existing_session = await crud.get_session_by_id(db, session_id=session_id)
        if existing_session and existing_session.user_id != current_user.id:
            existing_session = None

    if not existing_session:
        # Create new session with auto title from message snippet
        title = user_query[:30] + ("..." if len(user_query) > 30 else "")
        new_session = await crud.create_session(
            db,
            user_id=current_user.id,
            title=title or "New Conversation",
        )
        session_id = new_session.id

    # 2. Fetch prior conversation history before saving the current message
    prior_messages = await crud.get_recent_messages(db, session_id=session_id, limit=10)
    history_dicts = [
        {"role": msg.role, "content": msg.content}
        for msg in prior_messages
    ]

    # 3. Persist user message
    await crud.save_message(
        db,
        session_id=session_id,
        role="user",
        content=user_query,
        agent_name=None,
        intent=None,
    )

    # 4. Multi-Agent AI Orchestration
    intent_detector = get_intent_detector()
    router_agent = get_agent_router()
    aggregator = get_response_aggregator()

    # 4a. Detect intents
    t0 = time.time()
    detected_intents = await intent_detector.adetect(user_query, history=history_dicts)
    intent_duration = (time.time() - t0) * 1000
    logger.info(
        f"Session {session_id} | Intent detected in {intent_duration:.1f}ms: {detected_intents}"
    )

    # 4b. Route to specialized agents
    selected_agents = router_agent.route(detected_intents)
    agent_names = [a.name for a in selected_agents]
    logger.info(f"Session {session_id} | Routed to agents: {agent_names}")

    # 4c. Concurrent agent execution (Scoped RAG + LLM)
    t1 = time.time()
    agent_responses = await router_agent.dispatch_all(
        agents=selected_agents,
        query=user_query,
        history=history_dicts,
    )
    dispatch_duration = (time.time() - t1) * 1000
    logger.info(
        f"Session {session_id} | Agent execution completed in {dispatch_duration:.1f}ms"
    )

    # 4d. Synthesize response & aggregate citations
    t2 = time.time()
    aggregated_result = await aggregator.aaggregate(
        responses=agent_responses,
        query=user_query,
    )
    synthesis_duration = (time.time() - t2) * 1000

    # 5. Persist assistant response in DB
    primary_agent_name = ", ".join(aggregated_result.agents_invoked) if aggregated_result.agents_invoked else "faq"
    assistant_msg = await crud.save_message(
        db,
        session_id=session_id,
        role="assistant",
        content=aggregated_result.text,
        agent_name=primary_agent_name,
        intent=detected_intents,
    )

    # 6. Format source citations
    chat_sources = [
        ChatSource(
            document=s.get("document", "TechMart Knowledge Base"),
            page=s.get("page"),
        )
        for s in aggregated_result.sources
    ]

    total_pipeline_ms = (time.time() - pipeline_start) * 1000
    logger.log_pipeline_summary(
        session_id=str(session_id),
        intents=detected_intents,
        agents_invoked=aggregated_result.agents_invoked or ["faq"],
        total_duration_ms=total_pipeline_ms,
        response_length=len(aggregated_result.text),
    )

    return ChatResponse(
        message_id=assistant_msg.id,
        response=aggregated_result.text,
        agents_invoked=aggregated_result.agents_invoked or ["faq"],
        intent=detected_intents,
        session_id=session_id,
        timestamp=assistant_msg.created_at or datetime.now(timezone.utc),
        sources=chat_sources,
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
