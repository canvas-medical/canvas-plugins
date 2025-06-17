from collections.abc import Sequence
from decimal import Decimal, InvalidOperation

import pytest

from canvas_sdk.v1.data.utils import quantize


@pytest.mark.parametrize(
    argnames="input_value,expected",
    argvalues=[
        (Decimal("10.235"), Decimal("10.24")),
        (Decimal("10.234"), Decimal("10.23")),
        (10.236, Decimal("10.24")),
        (10.234, Decimal("10.23")),
        ("10.236", Decimal("10.24")),
        ("10.2", Decimal("10.20")),
        ((0, [1, 2, 3, 4, 5], -2), Decimal("123.45")),
        ((1, [0], 0), Decimal("-0.00")),
    ],
    ids=[
        "decimal",
        "decimal_round_down",
        "float_round_up",
        "float_round_down",
        "string_round_up",
        "string_round_down",
        "tuple_decimal",
        "tuple_int_zero",
    ],
)
def test_quantize_valid_inputs(
    input_value: Decimal | float | str | tuple[int, Sequence[int], int], expected: Decimal
) -> None:
    """Test quantization of various valid inputs."""
    assert quantize(input_value) == expected


def test_quantize_invalid_string() -> None:
    """Test quantization with an invalid string input."""
    with pytest.raises(InvalidOperation):
        quantize("invalid")


def test_quantize_invalid_type() -> None:
    """Test quantization with an unsupported type."""
    with pytest.raises(TypeError):
        quantize(object())  # type: ignore[arg-type]
