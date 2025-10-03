import random
import string
import uuid
from collections.abc import Sequence
from decimal import Decimal


def quantize(deci: Decimal | float | str | tuple[int, Sequence[int], int]) -> Decimal:
    """Rounds a Decimal value to two decimal places."""
    return Decimal(deci).quantize(Decimal(".01"))


def create_key() -> str:
    """Generates a unique key using UUID4."""
    return uuid.uuid4().hex


def generate_mrn(length: int = 9, max_attempts: int = 100) -> str:
    """Generates a unique Medical Record Number (MRN) of specified length."""
    from canvas_sdk.v1.data import Patient

    digits = string.digits

    for _ in range(max_attempts):
        mrn = "".join(random.choices(digits, k=length))
        if not Patient.objects.filter(mrn=mrn).exists():
            return mrn

    raise RuntimeError(f"Unable to generate a unique MRN after {max_attempts} attempts")


def empty_note_body() -> list[dict[str, str]]:
    """Generates an empty note body with 15 empty text elements."""
    return [{"type": "text", "value": ""}] * 15


__exports__ = ()
