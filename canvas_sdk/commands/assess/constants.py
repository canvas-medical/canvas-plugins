from enum import Enum


class AssessStatus(Enum):
    """Enum class for Assess status field."""

    IMPROVED = "improved"
    STABLE = "stable"
    DETERIORATED = "deteriorated"
