from enum import Enum


class RunStatus(Enum):
    """Status values for processor runs.

    PENDING: The run is queued and waiting to start.
    PROCESSING: The run is currently being processed.
    PROCESSED: The run has completed successfully.
    FAILED: The run encountered an error and failed.
    CANCELLED: The run was cancelled before completion.
    """

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


__exports__ = ()
