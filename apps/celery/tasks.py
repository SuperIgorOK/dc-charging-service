import asyncio
from datetime import datetime, timedelta, timezone
from celery import Celery

from apps.enums.station_enums import StationStatusEnum
from apps.repositories.station_repo import StationRepository
from apps.schemas.redis_schema import ConnectorStatusRedisModel
from apps.settings.database import get_session_context

celery = Celery(__name__)
celery.conf.broker_url = "redis://localhost:6379/0"


@celery.task(name="check_all_stations_availability")
def check_all_stations_availability():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(_check_all_stations_availability())


async def _check_all_stations_availability():
    timeout = datetime.now(timezone.utc) - timedelta(minutes=2)

    async with get_session_context() as session:
        station_repo = StationRepository(session)
        stations = await station_repo.get_all()

        for station in stations:
            station_id = station.id

            connectors = await ConnectorStatusRedisModel.find(
                ConnectorStatusRedisModel.station_id == str(station_id)
            ).all()

            if not connectors:
                continue

            all_expired = all(conn.updated_at < timeout for conn in connectors)

            if all_expired and station.status != StationStatusEnum.Unavailable:
                station.status = StationStatusEnum.Unavailable
                await station_repo.update(station)
