from unittest.mock import patch

from canvas_sdk.v1.data.business_line import BusinessLine


def test_logo_url_with_logo() -> None:
    """logo_url returns a presigned URL when a logo is set."""
    business_line = BusinessLine()
    business_line.logo = "logo.png"

    with patch(
        "canvas_sdk.v1.data.business_line.presigned_url",
        return_value="https://s3.example.com/presigned",
    ) as mock:
        assert business_line.logo_url == "https://s3.example.com/presigned"
        mock.assert_called_once_with("logo.png")


def test_logo_url_returns_none_when_unset() -> None:
    """logo_url returns None when no logo is set."""
    business_line = BusinessLine()
    business_line.logo = ""

    assert business_line.logo_url is None
