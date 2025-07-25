from datetime import datetime
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from apps.enums.session_enums import SessionStatusEnum
from apps.models import Session


class SessionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, session_id: int) -> Session | None:
        stmt = select(Session).where(Session.id == session_id)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_session(
        self, station_id: UUID, connector_number: int
    ) -> Session | None:
        stmt = select(Session).where(
            Session.station_id == station_id,
            Session.connector_number == connector_number,
            Session.end_time.is_(None),
            Session.status.in_(
                [SessionStatusEnum.started, SessionStatusEnum.in_progress]
            ),
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def start_session(
        self,
        station_id: UUID,
        connector_number: int,
        start_time: datetime,
        status: SessionStatusEnum,
    ) -> Session:
        session = Session(
            station_id=station_id,
            connector_number=connector_number,
            start_time=start_time,
            status=status,
        )
        self.db.add(session)
        await self.db.flush()
        return session

    async def end_session(
        self,
        session: Session,
        end_time: datetime,
        status: SessionStatusEnum,
    ) -> Session:
        session.end_time = end_time
        session.status = status

        await self.db.flush()
        return session

    async def get_sessions_by_station(
        self,
        station_id: UUID,
        time_from: datetime | None = None,
        time_to: datetime | None = None,
        offset: int = 0,
        limit: int = 100,
    ) -> list[Session]:
        stmt = select(Session).where(Session.station_id == station_id)

        if time_from:
            stmt = stmt.where(Session.start_time >= time_from)
        if time_to:
            stmt = stmt.where(Session.start_time <= time_to)

        stmt = stmt.order_by(Session.start_time.desc())
        stmt = stmt.offset(offset).limit(limit)

        result = await self.db.execute(stmt)
        return result.scalars().all()
