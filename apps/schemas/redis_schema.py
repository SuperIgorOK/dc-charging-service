from datetime import datetime
from typing import Literal

from aredis_om import JsonModel, Field, get_redis_connection

from apps.settings.config import get_settings

settings = get_settings()

REDIS_CONNECTION = get_redis_connection(
    url=f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
)


class ConnectorStatusRedisModel(JsonModel):
    station_id: str = Field(index=True)
    connector_number: int = Field(index=True, primary_key=True)
    status: Literal["available", "occupied", "fault", "unknown"]
    updated_at: datetime

    class Meta:
        global_key_prefix = "connector_status"
        database = REDIS_CONNECTION
