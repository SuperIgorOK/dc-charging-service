from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from apps.settings.dependencies import get_async_session
from apps.services.session_service import SessionService
from apps.schemas.session_schemas import SessionResponse

router = APIRouter()


@router.get("/{station_id}/sessions", response_model=list[SessionResponse])
async def get_sessions_by_station(
    station_id: UUID,
    time_from: Optional[datetime] = Query(None, alias="from"),
    time_to: Optional[datetime] = Query(None, alias="to"),
    offset: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_async_session),
):
    sessions = await SessionService(db).get_sessions_by_station(
        station_id=station_id,
        time_from=time_from,
        time_to=time_to,
        offset=offset,
        limit=limit,
    )

    return sessions
