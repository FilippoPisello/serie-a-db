"""Values shared across multiple data sources."""

from enum import StrEnum


class Status(StrEnum):
    """Match day status."""

    COMPLETED = "completed"
    ONGOING = "ongoing"
    UPCOMING = "upcoming"
