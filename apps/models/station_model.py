import uuid

from sqlalchemy import UUID
from sqlalchemy.orm import Mapped, relationship, mapped_column

from apps.enums.station_enums import StationStatusEnum
from apps.settings.database import Base


class Station(Base):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str | None] = mapped_column()
    max_input_power: Mapped[int] = mapped_column(server_default="240")
    status: Mapped[StationStatusEnum] = mapped_column(
        default=StationStatusEnum.Available
    )

    sessions: Mapped[list["Session"]] = relationship()
