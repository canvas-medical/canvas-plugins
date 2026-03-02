import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from canvas_sdk.utils.pdf import PdfAuthRequest, pdf_generator


class FakeResponse:
    """A mock requests.Response."""

    def __init__(
        self,
        status_code: int = 200,
        content: bytes = b"",
        headers: dict[str, str] | None = None,
    ) -> None:
        self.status_code = status_code
        self.content = content
        self.headers = headers or {}

    def json(self) -> dict[str, Any]:
        """Return the fake json response."""
        return {"abc": 123}


@patch("canvas_sdk.utils.pdf.CUSTOMER_IDENTIFIER", "test-customer")
@patch.dict(os.environ, {"CANVAS_PUBLIC_HOST": ""})
@patch("requests.Session.get")
def test_pdf_from_url(mock_get: MagicMock) -> None:
    """Test that from_url returns a PdfUrlResponse on 302 redirect."""
    mock_get.return_value = FakeResponse(
        status_code=302,
        headers={"Location": "https://s3.amazonaws.com/bucket/file.pdf"},
    )

    response = pdf_generator.from_url("/print/note/123/")

    mock_get.assert_called_once_with(
        "https://web-to-pdf.canvasmedical.com/generate/?customerId=test-customer&url=%2Fprint%2Fnote%2F123%2F",
        headers={},
        timeout=30,
        allow_redirects=False,
    )

    assert response is not None
    assert response.url == "https://s3.amazonaws.com/bucket/file.pdf"


@patch("canvas_sdk.utils.pdf.CUSTOMER_IDENTIFIER", "test-customer")
@patch.dict(os.environ, {"CANVAS_PUBLIC_HOST": ""})
@patch("requests.Session.get")
def test_pdf_from_url_with_auth(mock_get: MagicMock) -> None:
    """Test that PdfAuthRequest propagates auth headers."""
    mock_get.return_value = FakeResponse(
        status_code=302,
        headers={"Location": "https://s3.amazonaws.com/bucket/file.pdf"},
    )

    auth = PdfAuthRequest(username="user", password="pass")
    pdf_generator.from_url("/print/note/123/", auth=auth)

    mock_get.assert_called_once_with(
        "https://web-to-pdf.canvasmedical.com/generate/?customerId=test-customer&url=%2Fprint%2Fnote%2F123%2F",
        headers={"X-PDF-Auth-User": "user", "X-PDF-Auth-Password": "pass"},
        timeout=30,
        allow_redirects=False,
    )


@patch("canvas_sdk.utils.pdf.CUSTOMER_IDENTIFIER", "test-customer")
@patch.dict(os.environ, {"CANVAS_PUBLIC_HOST": "https://myinstance.canvasmedical.com"})
@patch("requests.Session.get")
def test_pdf_from_url_with_host(mock_get: MagicMock) -> None:
    """Test that CANVAS_PUBLIC_HOST env var is prepended to the print URL."""
    mock_get.return_value = FakeResponse(
        status_code=302,
        headers={"Location": "https://s3.amazonaws.com/bucket/file.pdf"},
    )

    pdf_generator.from_url("/print/note/123/")

    mock_get.assert_called_once_with(
        "https://web-to-pdf.canvasmedical.com/generate/?customerId=test-customer&url=https%3A%2F%2Fmyinstance.canvasmedical.com%2Fprint%2Fnote%2F123%2F",
        headers={},
        timeout=30,
        allow_redirects=False,
    )


@patch("canvas_sdk.utils.pdf.CUSTOMER_IDENTIFIER", "test-customer")
@patch.dict(os.environ, {"CANVAS_PUBLIC_HOST": "https://myinstance.canvasmedical.com"})
@patch("requests.Session.get")
def test_pdf_from_url_normalizes_slashes(mock_get: MagicMock) -> None:
    """Test that a missing leading slash on print_url is handled correctly."""
    mock_get.return_value = FakeResponse(
        status_code=302,
        headers={"Location": "https://s3.amazonaws.com/bucket/file.pdf"},
    )

    pdf_generator.from_url("plugin-io/api/some-plugin/printout/html?note_uuid=abc")

    mock_get.assert_called_once_with(
        "https://web-to-pdf.canvasmedical.com/generate/?customerId=test-customer&url=https%3A%2F%2Fmyinstance.canvasmedical.com%2Fplugin-io%2Fapi%2Fsome-plugin%2Fprintout%2Fhtml%3Fnote_uuid%3Dabc",
        headers={},
        timeout=30,
        allow_redirects=False,
    )


@patch("canvas_sdk.utils.pdf.CUSTOMER_IDENTIFIER", "test-customer")
@patch.dict(os.environ, {"CANVAS_PUBLIC_HOST": ""})
@patch("requests.Session.get")
def test_pdf_from_url_non_redirect_returns_none(mock_get: MagicMock) -> None:
    """Test that a non-302 response returns None."""
    mock_get.return_value = FakeResponse(status_code=200)

    response = pdf_generator.from_url("/print/note/123/")

    assert response is None


@patch("canvas_sdk.utils.pdf.CUSTOMER_IDENTIFIER", "test-customer")
@patch.dict(os.environ, {"CANVAS_PUBLIC_HOST": ""})
@patch("requests.Session.get")
def test_pdf_from_url_no_location_returns_none(mock_get: MagicMock) -> None:
    """Test that a 302 without Location header returns None."""
    mock_get.return_value = FakeResponse(status_code=302)

    response = pdf_generator.from_url("/print/note/123/")

    assert response is None


@patch("canvas_sdk.utils.pdf.CUSTOMER_IDENTIFIER", "test-customer")
@patch("requests.Session.post")
def test_pdf_from_html(mock_post: MagicMock) -> None:
    """Test that from_html returns a PdfUrlResponse on 302 redirect."""
    mock_post.return_value = FakeResponse(
        status_code=302,
        headers={"Location": "https://s3.amazonaws.com/bucket/file.pdf"},
    )

    response = pdf_generator.from_html("<html><body>Hello</body></html>")

    mock_post.assert_called_once_with(
        "https://web-to-pdf.canvasmedical.com/generate/?customerId=test-customer",
        data="<html><body>Hello</body></html>",
        headers={"Content-Type": "text/html"},
        timeout=30,
        allow_redirects=False,
    )

    assert response is not None
    assert response.url == "https://s3.amazonaws.com/bucket/file.pdf"


@patch("canvas_sdk.utils.pdf.CUSTOMER_IDENTIFIER", "test-customer")
@patch("requests.Session.post")
def test_pdf_from_html_non_redirect_returns_none(mock_post: MagicMock) -> None:
    """Test that a non-302 response from from_html returns None."""
    mock_post.return_value = FakeResponse(status_code=500)

    response = pdf_generator.from_html("<html><body>Hello</body></html>")

    assert response is None


def test_pdf_get_raises() -> None:
    """Test that PdfGenerator.get raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        pdf_generator.get("some-endpoint/")


def test_pdf_post_raises() -> None:
    """Test that PdfGenerator.post raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        pdf_generator.post("some-endpoint/")


def test_pdf_put_raises() -> None:
    """Test that PdfGenerator.put raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        pdf_generator.put("some-endpoint/")


def test_pdf_patch_raises() -> None:
    """Test that PdfGenerator.patch raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        pdf_generator.patch("some-endpoint/")
