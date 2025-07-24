from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from apps.enums.session_enums import SessionStatusEnum
from apps.repositories.session_repo import SessionRepository
from apps.models import Session


class SessionService:
    def __init__(self, db: AsyncSession):
        self.repo = SessionRepository(db)

    async def start_session(
        self, station_id: UUID, connector_number: int, start_time: datetime
    ) -> Session:
        return await self.repo.start_session(
            station_id=station_id,
            connector_number=connector_number,
            start_time=start_time,
            status=SessionStatusEnum.started,
        )

    async def end_session(
        self, session: Session, end_time: datetime, status: SessionStatusEnum
    ) -> None:
        await self.repo.end_session(session, end_time, status)

    async def get_active_session(
        self, station_id: UUID, connector_number: int
    ) -> Session | None:
        return await self.repo.get_active_session(station_id, connector_number)

    async def get_sessions_by_station(
        self,
        station_id: UUID,
        time_from: datetime | None = None,
        time_to: datetime | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Session]:
        return await self.repo.get_sessions_by_station(
            station_id, time_from, time_to, offset, limit
        )
