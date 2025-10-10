from enum import Enum


class RecurrenceEnum(Enum):
    DAYS = "Day(s)"
    WEEKS = "Week(s)"
    MONTHS = "Month(s)"
    NONE = "None"

FIELD_RECURRENCE_INTERVAL_KEY = "recurrence_interval"
FIELD_RECURRENCE_TYPE_KEY = "recurrence"
FIELD_RECURRENCE_STOP_AFTER_KEY = "stop_after"