from collections.abc import Sequence
from decimal import Decimal, InvalidOperation
from unittest.mock import MagicMock, patch

import pytest
from pytest_django.fixtures import SettingsWrapper

from canvas_sdk.v1.data.utils import generate_mrn, presigned_url, quantize


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


def test_presigned_url_generates_valid_url(settings: SettingsWrapper) -> None:
    """Test that presigned_url generates a valid URL with expected components."""
    settings.AWS_ACCESS_KEY_ID = "test-access-key"
    settings.AWS_SECRET_ACCESS_KEY = "test-secret-key"
    settings.MEDIA_S3_BUCKET_NAME = "test-bucket"
    settings.AWS_REGION = "us-west-2"

    url = presigned_url("path/to/file.pdf")

    assert url.startswith("https://test-bucket.s3.us-west-2.amazonaws.com/")
    assert "/path/to/file.pdf?" in url
    assert "X-Amz-Algorithm=AWS4-HMAC-SHA256" in url
    assert "X-Amz-Credential=" in url
    assert "X-Amz-Date=" in url
    assert "X-Amz-Expires=3600" in url
    assert "X-Amz-SignedHeaders=host" in url
    assert "X-Amz-Signature=" in url


def test_presigned_url_with_custom_expiry(settings: SettingsWrapper) -> None:
    """Test that presigned_url respects custom expiry time."""
    settings.AWS_ACCESS_KEY_ID = "test-access-key"
    settings.AWS_SECRET_ACCESS_KEY = "test-secret-key"
    settings.MEDIA_S3_BUCKET_NAME = "test-bucket"
    settings.AWS_REGION = "us-west-2"

    url = presigned_url("path/to/file.pdf", expires_in=7200)

    assert "X-Amz-Expires=7200" in url


def test_presigned_url_removes_bucket_prefix(settings: SettingsWrapper) -> None:
    """Test that presigned_url removes bucket prefix from key."""
    settings.AWS_ACCESS_KEY_ID = "test-access-key"
    settings.AWS_SECRET_ACCESS_KEY = "test-secret-key"
    settings.MEDIA_S3_BUCKET_NAME = "test-bucket"
    settings.AWS_REGION = "us-west-2"

    url = presigned_url("test-bucket/path/to/file.pdf")

    # The bucket prefix should be removed, so path should be /path/to/file.pdf
    assert "/path/to/file.pdf?" in url
    assert "/test-bucket/path/to/file.pdf?" not in url


def test_presigned_url_raises_error_without_credentials(settings: SettingsWrapper) -> None:
    """Test that presigned_url raises ValueError when AWS credentials are missing."""
    settings.AWS_ACCESS_KEY_ID = ""
    settings.AWS_SECRET_ACCESS_KEY = ""
    settings.MEDIA_S3_BUCKET_NAME = "test-bucket"
    settings.AWS_REGION = "us-west-2"

    with pytest.raises(ValueError, match="AWS credentials not configured"):
        presigned_url("path/to/file.pdf")
