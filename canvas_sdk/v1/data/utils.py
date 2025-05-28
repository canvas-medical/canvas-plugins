from collections.abc import Sequence
from decimal import Decimal


def quantize(deci: Decimal | float | str | tuple[int, Sequence[int], int]) -> Decimal:
    """Rounds a Decimal value to two decimal places."""
    return Decimal(deci).quantize(Decimal(".01"))


__exports__ = ()
