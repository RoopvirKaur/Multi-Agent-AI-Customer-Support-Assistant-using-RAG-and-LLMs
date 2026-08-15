"""
Database CRUD Operations
Asynchronous helper functions for users, sessions, messages, and analytics.
"""

import uuid
from typing import List, Optional, Sequence
from datetime import datetime
from sqlalchemy import select, update, delete, desc
from sqlalchemy.ext.asyncio import AsyncSession
from backend.database.models import User, Session, Message, AnalyticsEvent


# ============================================================
# User Operations
# ============================================================

async def create_user(
    db: AsyncSession,
    email: str,
    password_hash: str,
    name: Optional[str] = None,
) -> User:
    """Create and persist a new user."""
    user = User(
        email=email.strip().lower(),
        password_hash=password_hash,
        name=name.strip() if name else None,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def get_user_by_email(
    db: AsyncSession,
    email: str,
) -> Optional[User]:
    """Retrieve a user by their unique email address."""
    result = await db.execute(
        select(User).where(User.email == email.strip().lower())
    )
    return result.scalar_one_or_none()


async def get_user_by_id(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> Optional[User]:
    """Retrieve a user by their UUID primary key."""
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    return result.scalar_one_or_none()


# ============================================================
# Session Operations
# ============================================================

async def create_session(
    db: AsyncSession,
    user_id: uuid.UUID,
    title: Optional[str] = "New Conversation",
) -> Session:
    """Create a new conversation session for a user."""
    session = Session(
        user_id=user_id,
        title=title or "New Conversation",
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_sessions_by_user(
    db: AsyncSession,
    user_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
) -> Sequence[Session]:
    """Get all conversation sessions belonging to a user, newest first."""
    result = await db.execute(
        select(Session)
        .where(Session.user_id == user_id)
        .order_by(desc(Session.updated_at))
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def get_session_by_id(
    db: AsyncSession,
    session_id: uuid.UUID,
) -> Optional[Session]:
    """Get a conversation session by its ID."""
    result = await db.execute(
        select(Session).where(Session.id == session_id)
    )
    return result.scalar_one_or_none()


async def update_session_title(
    db: AsyncSession,
    session_id: uuid.UUID,
    title: str,
) -> Optional[Session]:
    """Update the title of an existing conversation session."""
    await db.execute(
        update(Session)
        .where(Session.id == session_id)
        .values(title=title, updated_at=datetime.utcnow())
    )
    await db.commit()
    return await get_session_by_id(db, session_id)


async def delete_session(
    db: AsyncSession,
    session_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    """Delete a session (and cascading messages) if it belongs to user_id."""
    result = await db.execute(
        delete(Session).where(
            Session.id == session_id,
            Session.user_id == user_id,
        )
    )
    await db.commit()
    return result.rowcount > 0


# ============================================================
# Message Operations
# ============================================================

async def save_message(
    db: AsyncSession,
    session_id: uuid.UUID,
    role: str,
    content: str,
    agent_name: Optional[str] = None,
    intent: Optional[List[str]] = None,
) -> Message:
    """
    Save a message (user or assistant) and refresh the session's updated_at timestamp.
    """
    message = Message(
        session_id=session_id,
        role=role,
        content=content,
        agent_name=agent_name,
        intent=intent,
    )
    db.add(message)

    # Touch session updated_at timestamp
    await db.execute(
        update(Session)
        .where(Session.id == session_id)
        .values(updated_at=datetime.utcnow())
    )

    await db.commit()
    await db.refresh(message)
    return message


async def get_messages_by_session(
    db: AsyncSession,
    session_id: uuid.UUID,
    limit: int = 100,
    offset: int = 0,
) -> Sequence[Message]:
    """Retrieve full message history for a session, chronologically ordered."""
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.asc())
        .limit(limit)
        .offset(offset)
    )
    return result.scalars().all()


async def get_recent_messages(
    db: AsyncSession,
    session_id: uuid.UUID,
    limit: int = 10,
) -> Sequence[Message]:
    """Retrieve the most recent N messages for context building (in chronological order)."""
    result = await db.execute(
        select(Message)
        .where(Message.session_id == session_id)
        .order_by(Message.created_at.desc())
        .limit(limit)
    )
    messages = list(result.scalars().all())
    messages.reverse()  # Return in chronological order
    return messages


# ============================================================
# Analytics Operations
# ============================================================

async def save_analytics_event(
    db: AsyncSession,
    session_id: Optional[uuid.UUID],
    event_type: str,
    payload: Optional[dict] = None,
) -> AnalyticsEvent:
    """Record an analytics or telemetry event."""
    event = AnalyticsEvent(
        session_id=session_id,
        event_type=event_type,
        payload=payload,
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    return event
