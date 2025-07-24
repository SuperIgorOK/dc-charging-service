from enum import Enum


class StationStatusEnum(str, Enum):
    NoConnect = "NoConnect"
    Available = "Available"
    Faulted = "Faulted"
    Unavailable = "Unavailable"
