from enum import Enum


class RecurrenceEnum(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    NONE = "none"

FIELD_RECURRENCE_KEY = "recurrence"