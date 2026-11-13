from collections.abc import Sequence
from decimal import Decimal, InvalidOperation
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlsplit

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
    settings.CUSTOMER_IDENTIFIER = "test-customer"

    url = presigned_url("path/to/file.pdf")

    assert url.startswith("https://test-bucket.s3.us-west-2.amazonaws.com/")
    assert "/test-customer/path/to/file.pdf?" in url
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
    settings.CUSTOMER_IDENTIFIER = "test-customer"

    url = presigned_url("path/to/file.pdf", expires_in=7200)

    assert "X-Amz-Expires=7200" in url


def test_presigned_url_removes_bucket_prefix(settings: SettingsWrapper) -> None:
    """Test that presigned_url removes bucket prefix from key."""
    settings.AWS_ACCESS_KEY_ID = "test-access-key"
    settings.AWS_SECRET_ACCESS_KEY = "test-secret-key"
    settings.MEDIA_S3_BUCKET_NAME = "test-bucket"
    settings.AWS_REGION = "us-west-2"
    settings.CUSTOMER_IDENTIFIER = "test-customer"

    url = presigned_url("test-bucket/path/to/file.pdf")

    # The bucket prefix should be removed, so path should be /test-customer/path/to/file.pdf
    assert "/test-customer/path/to/file.pdf?" in url
    assert "/test-bucket/path/to/file.pdf?" not in url


def test_presigned_url_raises_error_without_credentials(settings: SettingsWrapper) -> None:
    """Test that presigned_url raises ValueError when AWS credentials are missing."""
    settings.AWS_ACCESS_KEY_ID = ""
    settings.AWS_SECRET_ACCESS_KEY = ""
    settings.MEDIA_S3_BUCKET_NAME = "test-bucket"
    settings.AWS_REGION = "us-west-2"
    settings.CUSTOMER_IDENTIFIER = "test-customer"

    with pytest.raises(ValueError, match="AWS credentials not configured"):
        presigned_url("path/to/file.pdf")


@pytest.fixture
def signing_settings(settings: SettingsWrapper) -> SettingsWrapper:
    """Fixed credentials and bucket, matching the ones the reference URLs below were signed with."""
    settings.AWS_ACCESS_KEY_ID = "test-access-key"
    settings.AWS_SECRET_ACCESS_KEY = "test-secret-key"
    settings.MEDIA_S3_BUCKET_NAME = "test-bucket"
    settings.AWS_REGION = "us-west-2"
    settings.CUSTOMER_IDENTIFIER = "test-customer"
    return settings


def url_parts(url: str) -> tuple[str, dict[str, list[str]]]:
    """Split a URL into its path and its query parameters, so parameter order does not matter."""
    split = urlsplit(url)
    return split.path, parse_qs(split.query)


# Reference URLs signed by botocore's S3SigV4QueryAuth, AWS's own SigV4 implementation, with the
# credentials in signing_settings at 2026-11-13 12:00:00 UTC.
BOTOCORE_PLAIN_URL = (
    "https://test-bucket.s3.us-west-2.amazonaws.com/test-customer/path/to/file.pdf"
    "?X-Amz-Algorithm=AWS4-HMAC-SHA256"
    "&X-Amz-Credential=test-access-key%2F20261113%2Fus-west-2%2Fs3%2Faws4_request"
    "&X-Amz-Date=20261113T120000Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host"
    "&X-Amz-Signature=907fb67028ab57377c0a3944f210063934040ab9c2427165b1a5fbc44709d20b"
)
BOTOCORE_TYPED_URL = (
    "https://test-bucket.s3.us-west-2.amazonaws.com/test-customer/note_history/note_state_document_7"
    "?response-content-type=application%2Fpdf"
    "&response-content-disposition=inline%3B%20filename%3D%22note_state_document_7.pdf%22"
    "&X-Amz-Algorithm=AWS4-HMAC-SHA256"
    "&X-Amz-Credential=test-access-key%2F20261113%2Fus-west-2%2Fs3%2Faws4_request"
    "&X-Amz-Date=20261113T120000Z&X-Amz-Expires=3600&X-Amz-SignedHeaders=host"
    "&X-Amz-Signature=0ea615aa8f1bef7f3857d29b4be9f26e28ba3e1441e403e9087b858d1bfa1958"
)


@pytest.mark.freeze_time("2026-11-13 12:00:00")
def test_presigned_url_signature_matches_botocore(signing_settings: SettingsWrapper) -> None:
    """The signature matches the one AWS's own signer produces for the same request."""
    assert url_parts(presigned_url("path/to/file.pdf")) == url_parts(BOTOCORE_PLAIN_URL)


@pytest.mark.freeze_time("2026-11-13 12:00:00")
def test_presigned_url_names_and_types_a_key_without_an_extension(
    signing_settings: SettingsWrapper,
) -> None:
    """A key with no extension is signed with response overrides for its type and filename."""
    url = presigned_url("note_history/note_state_document_7", content_type="application/pdf")

    assert url_parts(url) == url_parts(BOTOCORE_TYPED_URL)


@pytest.mark.parametrize(
    "s3_key,content_type",
    [
        ("path/to/file.pdf", "application/pdf"),
        ("path/to/file", None),
        ("path/to/file", "application/x-unknown"),
    ],
    ids=["has-extension", "no-content-type", "unrecognized-content-type"],
)
def test_presigned_url_signs_without_response_overrides(
    signing_settings: SettingsWrapper, s3_key: str, content_type: str | None
) -> None:
    """A key that has an extension, or whose type gives none, is signed with no overrides."""
    _, query = url_parts(presigned_url(s3_key, content_type=content_type))

    assert [key for key in query if key.startswith("response-")] == []
