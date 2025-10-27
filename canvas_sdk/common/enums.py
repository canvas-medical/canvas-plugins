from enum import StrEnum


class TaskPriority(StrEnum):
    """Task priority values used across the SDK. Matches canvas-core values."""
    STAT = "stat"
    URGENT = "urgent"
    ROUTINE = "routine"


__exports__ = (
    "TaskPriority",
)

