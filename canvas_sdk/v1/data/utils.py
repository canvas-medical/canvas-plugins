import uuid
from collections.abc import Sequence
from decimal import Decimal


def quantize(deci: Decimal | float | str | tuple[int, Sequence[int], int]) -> Decimal:
    """Rounds a Decimal value to two decimal places."""
    return Decimal(deci).quantize(Decimal(".01"))


def create_key() -> str:
    """Generates a unique key using UUID4."""
    return uuid.uuid4().hex


__exports__ = ()
