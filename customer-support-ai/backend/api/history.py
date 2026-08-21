"""
History API Endpoints
Routes: /api/history/{session_id}
"""

import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.connection import get_db
from backend.database import crud
from backend.database.models import User
from backend.models.message import MessageOut
from backend.middleware.auth_middleware import get_current_user

router = APIRouter(prefix="/history", tags=["History"])


@router.get(
    "/{session_id}",
    response_model=List[MessageOut],
    summary="Get full conversation history for a session",
)
async def get_session_history(
    session_id: uuid.UUID,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve message history for a specific conversation session.
    Verifies that the session belongs to the requesting user.
    """
    session = await crud.get_session_by_id(db, session_id=session_id)
    if not session or session.user_id != current_user.id:
        return []

    messages = await crud.get_messages_by_session(
        db,
        session_id=session_id,
        limit=limit,
        offset=offset,
    )
    return [MessageOut.model_validate(m) for m in messages]
