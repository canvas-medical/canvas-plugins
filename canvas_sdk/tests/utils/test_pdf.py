import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests

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


@pytest.mark.parametrize(
    "method",
    ["get", "post", "put", "patch", "delete", "batch_requests", "join_url"],
)
def test_pdf_generator_has_no_raw_request_methods(method: str) -> None:
    """The PDF client exposes only its purpose-built methods."""
    assert not hasattr(pdf_generator, method)


def test_pdf_generator_exports_only_its_generators() -> None:
    """Plugin code can reach `from_url` and `from_html` and nothing else."""
    assert type(pdf_generator).__exports__ == ("from_url", "from_html")


def _failing_request(*args: Any, **kwargs: Any) -> None:
    request = requests.Request("POST", "https://web-to-pdf.canvasmedical.com/x").prepare()
    request.headers["Authorization"] = "test-credential"
    raise requests.Timeout("timed out", request=request)


@pytest.mark.parametrize(
    "call",
    [
        pytest.param(lambda: pdf_generator.from_html("<p>x</p>"), id="from_html"),
        pytest.param(lambda: pdf_generator.from_url("/print/x"), id="from_url"),
    ],
)
@patch("requests.Session.post", side_effect=_failing_request)
@patch("requests.Session.get", side_effect=_failing_request)
def test_pdf_generator_errors_are_plain_request_exceptions(
    _mock_get: MagicMock, _mock_post: MagicMock, call: Any
) -> None:
    """A failed request is re-raised as a plain RequestException, with nothing chained."""
    with pytest.raises(requests.RequestException) as excinfo:
        call()

    error = excinfo.value
    assert error.request is None
    assert error.__cause__ is None
    assert error.__context__ is None
