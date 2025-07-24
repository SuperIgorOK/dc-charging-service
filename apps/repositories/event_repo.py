from datetime import datetime
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.models import Event


class EventRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add_event(
        self, session_id: uuid.UUID, timestamp: datetime, event_type: str
    ) -> Event:
        event = Event(
            session_id=session_id,
            timestamp=timestamp,
            event_type=event_type,
        )
        self.db.add(event)
        await self.db.commit()
        return event

    async def get_by_session_id(self, session_id: uuid.UUID) -> list[Event]:
        result = await self.db.execute(
            select(Event).where(Event.session_id == session_id)
        )
        return result.scalars().all()
