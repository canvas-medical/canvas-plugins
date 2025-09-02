from enum import StrEnum


class TaskPriority(StrEnum):
    """Task priority values used across the SDK."""
    
    STAT = "STAT"
    URGENT = "Urgent"
    ROUTINE = "Routine"

__exports__ = (
    "TaskPriority",
)