from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from apps.repositories.event_repo import EventRepository


class EventService:
    def __init__(self, db: AsyncSession):
        self.repo = EventRepository(db)

    async def add_event(self, session_id: int, timestamp: datetime, event_type: str):
        await self.repo.add_event(session_id, timestamp, event_type)
