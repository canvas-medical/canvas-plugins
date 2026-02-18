from enum import Enum


class CriterionOperation(Enum):
    """Comparison operations for SendGrid query criteria."""

    GREATER_THAN = ">"
    GREATER_THAN_OR_EQUAL = ">="
    LOWER_THAN = "<"
    LOWER_THAN_OR_EQUAL = "<="
    EQUAL = "="


__exports__ = ()
