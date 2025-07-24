from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from apps.settings.dependencies import get_async_session
from apps.schemas.station_schemas import StationStatusResponse
from apps.services.station_service import StationService

router = APIRouter(
    prefix="/stations",
    tags=["Stations"],
    responses={404: {"description": "Not found"}},
)


@router.get("/{station_id}")
async def get_stations(
    station_id: str, db: AsyncSession = Depends(get_async_session)
) -> StationStatusResponse:
    return await StationService(db).get_station_status(station_id)
