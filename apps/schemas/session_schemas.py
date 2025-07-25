from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from apps.enums.session_enums import SessionStatusEnum


class SessionResponse(BaseModel):
    id: int
    station_id: UUID
    connector_number: int
    status: SessionStatusEnum
    start_time: datetime
    end_time: datetime | None

    model_config = ConfigDict(
        from_attributes=True,
    )
