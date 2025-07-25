from enum import Enum


class SessionStatusEnum(str, Enum):
    started = "started"
    in_progress = "in_progress"
    finished = "finished"
    error = "error"
