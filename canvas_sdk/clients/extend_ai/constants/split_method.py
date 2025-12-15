from enum import Enum


class SplitMethod(Enum):
    """Methods for splitting documents.

    HIGH_PRECISION: More accurate splitting at the cost of higher processing time.
    LOW_LATENCY: Faster splitting with potentially lower accuracy.
    """

    HIGH_PRECISION = "high_precision"
    LOW_LATENCY = "low_latency"


__exports__ = ()
