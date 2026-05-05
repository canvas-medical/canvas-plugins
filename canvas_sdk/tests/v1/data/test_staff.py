from unittest.mock import patch

from canvas_sdk.v1.data.staff import Staff


def test_signature_url_with_signature() -> None:
    """signature_url returns a presigned URL when signature is set."""
    staff = Staff()
    staff.signature = "signatures/staff_abc.png"

    with patch(
        "canvas_sdk.v1.data.staff.presigned_url",
        return_value="https://s3.example.com/presigned",
    ) as mock:
        assert staff.signature_url == "https://s3.example.com/presigned"
        mock.assert_called_once_with("signatures/staff_abc.png")


def test_signature_url_returns_none_when_empty() -> None:
    """signature_url returns None when signature is empty."""
    staff = Staff()
    staff.signature = ""

    assert staff.signature_url is None


def test_signature_url_returns_none_when_null() -> None:
    """signature_url returns None when signature is None."""
    staff = Staff()
    staff.signature = None

    assert staff.signature_url is None
