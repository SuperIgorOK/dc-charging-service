from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from apps.models import Station
from apps.repositories.station_repo import StationRepository
from apps.schemas.station_schemas import StationStatusResponse, ConnectorStatus
from apps.schemas.redis_schema import ConnectorStatusRedisModel


class StationService:
    def __init__(self, db: AsyncSession):
        self.station_repo = StationRepository(db)

    async def get_station_status(self, station_id: UUID) -> StationStatusResponse:
        station = await self.station_repo.get(station_id)
        if not station:
            raise ValueError("Station not found")

        # Поиск всех коннекторов этой станции
        connector_objects = await ConnectorStatusRedisModel.find(
            ConnectorStatusRedisModel.station_id == station_id
        ).all()

        connector_statuses = [
            ConnectorStatus(
                connector_number=conn.connector_number,
                status=conn.status,
                updated_at=conn.updated_at,
            )
            for conn in connector_objects
        ]

        return StationStatusResponse(
            station_id=str(station.id),
            name=station.name,
            status=station.status,
            connectors=sorted(
                connector_statuses,
                key=lambda conn: conn.connector_number,
            ),
        )

    async def get(self, station_id: UUID) -> Station | None:
        station = await self.station_repo.get(station_id)
        return station

    async def get_or_create(self, station_id: UUID) -> Station:
        station = await self.station_repo.get_or_create(station_id)
        return station

    async def update(self, station: Station) -> None:
        await self.station_repo.update(station)

    async def get_all(self) -> list[Station]:
        return await self.station_repo.get_all()
