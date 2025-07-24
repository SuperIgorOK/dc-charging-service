from typing import Literal

from pydantic import BaseModel
from datetime import datetime


class ConnectorStatus(BaseModel):
    connector_number: int
    status: Literal["available", "occupied", "fault", "unknown"]
    updated_at: datetime
