from enum import Enum


class EventTypeEnum(str, Enum):
    STARTED = "Started"
    ENDED = "Ended"
    FAULTED = "Faulted"
