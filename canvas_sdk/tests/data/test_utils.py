from collections.abc import Sequence
from decimal import Decimal, InvalidOperation
from unittest.mock import MagicMock, patch

import pytest

from canvas_sdk.v1.data.utils import generate_mrn, quantize


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


@patch("canvas_sdk.v1.data.Patient")
def test_generates_mrn_with_default_length(mock_patient: MagicMock) -> None:
    """Test that MRN is generated with default length of 9 digits."""
    mock_patient.objects.filter.return_value.exists.return_value = False

    mrn = generate_mrn()

    assert len(mrn) == 9
    assert mrn.isdigit()
    mock_patient.objects.filter.assert_called_once_with(mrn=mrn)


@patch("canvas_sdk.v1.data.Patient")
def test_generates_mrn_with_custom_length(mock_patient: MagicMock) -> None:
    """Test that MRN is generated with specified custom length."""
    mock_patient.objects.filter.return_value.exists.return_value = False

    for length in [5, 7, 12, 15]:
        mrn = generate_mrn(length=length)
        assert len(mrn) == length
        assert mrn.isdigit()


@patch("canvas_sdk.v1.data.Patient")
def test_generates_unique_mrn_when_first_attempt_exists(mock_patient: MagicMock) -> None:
    """Test that function tries again when first MRN already exists."""
    mock_patient.objects.filter.return_value.exists.side_effect = [True, False]

    mrn = generate_mrn()

    assert len(mrn) == 9
    assert mrn.isdigit()
    assert mock_patient.objects.filter.call_count == 2


@patch("canvas_sdk.v1.data.Patient")
def test_raises_runtime_error_after_max_attempts(mock_patient: MagicMock) -> None:
    """Test that RuntimeError is raised when max attempts are exceeded."""
    mock_patient.objects.filter.return_value.exists.return_value = True

    with pytest.raises(RuntimeError, match="Unable to generate a unique MRN after 100 attempts"):
        generate_mrn()

    assert mock_patient.objects.filter.call_count == 100
