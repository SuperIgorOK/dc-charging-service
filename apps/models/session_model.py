import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, DateTime
from sqlalchemy.orm import Mapped, relationship, mapped_column

from apps.settings.database import Base
from apps.enums.session_enums import SessionStatusEnum


class Session(Base):
    id: Mapped[int] = mapped_column(primary_key=True)
    station_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("stations.id", ondelete="CASCADE"),
        nullable=False,
    )
    connector_number: Mapped[int] = mapped_column()
    status: Mapped[SessionStatusEnum] = mapped_column()
    start_time: Mapped[datetime] = mapped_column(DateTime)
    end_time: Mapped[datetime | None] = mapped_column(DateTime)

    events: Mapped[list["Event"]] = relationship(back_populates="session")
