from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from apps.models import Station


class StationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, station_id: UUID) -> Station | None:
        stmt = select(Station).where(Station.id == station_id)
        result = await self.db.execute(stmt)
        return result.scalars().one_or_none()

    async def create(self, station_id: UUID) -> Station:
        station = Station(id=station_id)
        self.db.add(station)
        await self.db.flush()
        return station

    async def get_or_create(self, station_id: UUID) -> Station:
        existing = await self.get(station_id)
        if existing:
            return existing
        return await self.create(station_id)

    async def update(self, station: Station) -> None:
        self.db.add(station)
        await self.db.commit()

    async def get_all(self) -> list[Station]:
        result = await self.db.execute(select(Station))
        return result.scalars().all()
