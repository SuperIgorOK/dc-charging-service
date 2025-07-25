from uuid import UUID
from pydantic import BaseModel, Field
from apps.enums.station_enums import StationStatusEnum
from apps.schemas.connector_schemas import ConnectorStatus


class StationCreate(BaseModel):
    id: UUID = Field(..., description="UUID станции")
    name: str = Field(..., description="Название станции")
    max_input_power: int = Field(..., description="Макс. входная мощность, Вт")


class StationStatusResponse(BaseModel):
    station_id: str
    name: str | None
    status: StationStatusEnum
    connectors: list[ConnectorStatus]
