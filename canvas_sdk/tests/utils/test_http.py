import os
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from canvas_sdk.utils import Http
from canvas_sdk.utils.http import PdfAuthRequest, ontologies_http, pharmacy_http, web_to_pdf_http


class FakeResponse:
    """
    A mock requests.Response.
    """

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
        """
        Return a known response for mocking.
        """
        return {"abc": 123}


@patch("requests.Session.get")
def test_http_get_json(mock_get: MagicMock) -> None:
    """
    Test that the OntologiesHttp.get_json method calls requests.get with the correct arguments.
    """
    mock_get.return_value = FakeResponse()

    response = ontologies_http.get_json("/fdb/medication")

    mock_get.assert_called_once_with(
        "https://ontologies.canvasmedical.com/fdb/medication",
        headers={},
        timeout=30,
    )

    assert response.status_code == 200
    assert response.json() == {"abc": 123}


@pytest.mark.parametrize(
    ("headers", "exp_headers"),
    [
        pytest.param(
            {"Authorization": "Bearer as;ldkfjdkj"},
            {"Authorization": "Bearer as;ldkfjdkj"},
            id="with_headers",
        ),
        pytest.param(
            None,
            {},
            id="without_headers",
        ),
    ],
)
@patch("requests.Session.get")
def test_http_get(mock_get: MagicMock, headers: dict | None, exp_headers: dict) -> None:
    """Test that the Http.get method calls requests.get with the correct arguments."""
    http = Http()
    url = "https://www.canvasmedical.com/"
    http.get(url, headers=headers)
    mock_get.assert_called_once_with(url, headers=exp_headers, timeout=30)
    if headers is None:
        mock_get.reset_mock()
        http.get(url)
        mock_get.assert_called_once_with(url, headers=exp_headers, timeout=30)


@patch("requests.Session.post")
def test_http_post(mock_post: MagicMock) -> None:
    """Test that the Http.post method calls requests.post with the correct arguments."""
    http = Http()
    http.post(
        "https://www.canvasmedical.com/",
        json={"hey": "hi"},
        data="grant-type=client_credentials",
        headers={"Content-type": "application/json"},
    )
    mock_post.assert_called_once_with(
        "https://www.canvasmedical.com/",
        json={"hey": "hi"},
        data="grant-type=client_credentials",
        headers={"Content-type": "application/json"},
        timeout=30,
    )


@patch("requests.Session.put")
def test_http_put(mock_put: MagicMock) -> None:
    """Test that the Http.put method calls requests.put with the correct arguments."""
    http = Http()
    http.put(
        "https://www.canvasmedical.com/",
        json={"hey": "hi"},
        data="grant-type=client_credentials",
        headers={"Content-type": "application/json"},
    )
    mock_put.assert_called_once_with(
        "https://www.canvasmedical.com/",
        json={"hey": "hi"},
        data="grant-type=client_credentials",
        headers={"Content-type": "application/json"},
        timeout=30,
    )


@patch("requests.Session.patch")
def test_http_patch(mock_patch: MagicMock) -> None:
    """Test that the Http.patch method calls requests.patch with the correct arguments."""
    http = Http()
    http.patch(
        "https://www.canvasmedical.com/",
        json={"hey": "hi"},
        data="grant-type=client_credentials",
        headers={"Content-type": "application/json"},
    )
    mock_patch.assert_called_once_with(
        "https://www.canvasmedical.com/",
        json={"hey": "hi"},
        data="grant-type=client_credentials",
        headers={"Content-type": "application/json"},
        timeout=30,
    )


@pytest.mark.parametrize(
    ("headers", "exp_headers"),
    [
        pytest.param(
            {"Authorization": "Bearer as;ldkfjdkj"},
            {"Authorization": "Bearer as;ldkfjdkj"},
            id="with_headers",
        ),
        pytest.param(
            None,
            {},
            id="without_headers",
        ),
    ],
)
@patch("requests.Session.delete")
def test_http_delete(mock_delete: MagicMock, headers: dict | None, exp_headers: dict) -> None:
    """Test that the Http.delete method calls requests.delete with the correct arguments."""
    http = Http()
    url = "https://www.canvasmedical.com/"
    http.delete(url, headers=headers)
    mock_delete.assert_called_once_with(url, headers=exp_headers, timeout=30)
    if headers is None:
        mock_delete.reset_mock()
        http.delete(url)
        mock_delete.assert_called_once_with(url, headers=exp_headers, timeout=30)


@patch("requests.Session.get")
def test_search_pharmacies_default_search_term(mock_get: MagicMock) -> None:
    """
    Test that the PharmacyHttp.search_pharmacies method provides a default search term if one is not provided.
    """
    mock_get.return_value = FakeResponse()

    pharmacy_http.search_pharmacies()

    mock_get.assert_called_once_with(
        "https://pharmacy-2017071.canvasmedical.com/surescripts/pharmacy/?search=+",
        headers={},
        timeout=30,
    )

    pharmacy_http.search_pharmacies("abc123")

    mock_get.assert_called_with(
        "https://pharmacy-2017071.canvasmedical.com/surescripts/pharmacy/?search=abc123",
        headers={},
        timeout=30,
    )


@patch("canvas_sdk.utils.http.CUSTOMER_IDENTIFIER", "test-customer")
@patch.dict(os.environ, {"CANVAS_PUBLIC_HOST": ""})
@patch("requests.Session.get")
def test_web_to_pdf_generate_from_url(mock_get: MagicMock) -> None:
    """Test that generate_from_url returns a PdfUrlResponse on 302 redirect."""
    mock_get.return_value = FakeResponse(
        status_code=302,
        headers={"Location": "https://s3.amazonaws.com/bucket/file.pdf"},
    )

    response = web_to_pdf_http.generate_from_url("/print/note/123/")

    mock_get.assert_called_once_with(
        "https://web-to-pdf.canvasmedical.com/generate/?customerId=test-customer&url=%2Fprint%2Fnote%2F123%2F",
        headers={},
        timeout=30,
        allow_redirects=False,
    )

    assert response is not None
    assert response.url == "https://s3.amazonaws.com/bucket/file.pdf"
    assert response.status_code == 302


@patch("canvas_sdk.utils.http.CUSTOMER_IDENTIFIER", "test-customer")
@patch.dict(os.environ, {"CANVAS_PUBLIC_HOST": ""})
@patch("requests.Session.get")
def test_web_to_pdf_generate_from_url_with_auth(mock_get: MagicMock) -> None:
    """Test that PdfAuthRequest propagates auth headers."""
    mock_get.return_value = FakeResponse(
        status_code=302,
        headers={"Location": "https://s3.amazonaws.com/bucket/file.pdf"},
    )

    auth = PdfAuthRequest(username="user", password="pass")
    web_to_pdf_http.generate_from_url("/print/note/123/", auth=auth)

    mock_get.assert_called_once_with(
        "https://web-to-pdf.canvasmedical.com/generate/?customerId=test-customer&url=%2Fprint%2Fnote%2F123%2F",
        headers={"X-PDF-Auth-User": "user", "X-PDF-Auth-Password": "pass"},
        timeout=30,
        allow_redirects=False,
    )


@patch("canvas_sdk.utils.http.CUSTOMER_IDENTIFIER", "test-customer")
@patch.dict(os.environ, {"CANVAS_PUBLIC_HOST": "https://myinstance.canvasmedical.com"})
@patch("requests.Session.get")
def test_web_to_pdf_generate_from_url_with_host(mock_get: MagicMock) -> None:
    """Test that CANVAS_PUBLIC_HOST env var is prepended to the print URL."""
    mock_get.return_value = FakeResponse(
        status_code=302,
        headers={"Location": "https://s3.amazonaws.com/bucket/file.pdf"},
    )

    web_to_pdf_http.generate_from_url("/print/note/123/")

    mock_get.assert_called_once_with(
        "https://web-to-pdf.canvasmedical.com/generate/?customerId=test-customer&url=https%3A%2F%2Fmyinstance.canvasmedical.com%2Fprint%2Fnote%2F123%2F",
        headers={},
        timeout=30,
        allow_redirects=False,
    )


@patch("canvas_sdk.utils.http.CUSTOMER_IDENTIFIER", "test-customer")
@patch.dict(os.environ, {"CANVAS_PUBLIC_HOST": "https://myinstance.canvasmedical.com"})
@patch("requests.Session.get")
def test_web_to_pdf_generate_from_url_normalizes_slashes(mock_get: MagicMock) -> None:
    """Test that a missing leading slash on print_url is handled correctly."""
    mock_get.return_value = FakeResponse(
        status_code=302,
        headers={"Location": "https://s3.amazonaws.com/bucket/file.pdf"},
    )

    web_to_pdf_http.generate_from_url("plugin-io/api/some-plugin/printout/html?note_uuid=abc")

    mock_get.assert_called_once_with(
        "https://web-to-pdf.canvasmedical.com/generate/?customerId=test-customer&url=https%3A%2F%2Fmyinstance.canvasmedical.com%2Fplugin-io%2Fapi%2Fsome-plugin%2Fprintout%2Fhtml%3Fnote_uuid%3Dabc",
        headers={},
        timeout=30,
        allow_redirects=False,
    )


@patch("canvas_sdk.utils.http.CUSTOMER_IDENTIFIER", "test-customer")
@patch.dict(os.environ, {"CANVAS_PUBLIC_HOST": ""})
@patch("requests.Session.get")
def test_web_to_pdf_generate_from_url_non_redirect_returns_none(mock_get: MagicMock) -> None:
    """Test that a non-302 response returns None."""
    mock_get.return_value = FakeResponse(status_code=200)

    response = web_to_pdf_http.generate_from_url("/print/note/123/")

    assert response is None


@patch("canvas_sdk.utils.http.CUSTOMER_IDENTIFIER", "test-customer")
@patch.dict(os.environ, {"CANVAS_PUBLIC_HOST": ""})
@patch("requests.Session.get")
def test_web_to_pdf_generate_from_url_no_location_returns_none(mock_get: MagicMock) -> None:
    """Test that a 302 without Location header returns None."""
    mock_get.return_value = FakeResponse(status_code=302)

    response = web_to_pdf_http.generate_from_url("/print/note/123/")

    assert response is None


@patch("canvas_sdk.utils.http.CUSTOMER_IDENTIFIER", "test-customer")
@patch("requests.Session.post")
def test_web_to_pdf_generate_from_html(mock_post: MagicMock) -> None:
    """Test that generate_from_html returns a PdfUrlResponse on 302 redirect."""
    mock_post.return_value = FakeResponse(
        status_code=302,
        headers={"Location": "https://s3.amazonaws.com/bucket/file.pdf"},
    )

    response = web_to_pdf_http.generate_from_html("<html><body>Hello</body></html>")

    mock_post.assert_called_once_with(
        "https://web-to-pdf.canvasmedical.com/generate/?customerId=test-customer",
        data="<html><body>Hello</body></html>",
        headers={"Content-Type": "text/html"},
        timeout=30,
        allow_redirects=False,
    )

    assert response is not None
    assert response.url == "https://s3.amazonaws.com/bucket/file.pdf"
    assert response.status_code == 302


@patch("canvas_sdk.utils.http.CUSTOMER_IDENTIFIER", "test-customer")
@patch("requests.Session.post")
def test_web_to_pdf_generate_from_html_non_redirect_returns_none(mock_post: MagicMock) -> None:
    """Test that a non-302 response from generate_from_html returns None."""
    mock_post.return_value = FakeResponse(status_code=500)

    response = web_to_pdf_http.generate_from_html("<html><body>Hello</body></html>")

    assert response is None


def test_web_to_pdf_get_raises() -> None:
    """Test that WebToPdfHttp.get raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        web_to_pdf_http.get("some-endpoint/")


def test_web_to_pdf_post_raises() -> None:
    """Test that WebToPdfHttp.post raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        web_to_pdf_http.post("some-endpoint/")


def test_web_to_pdf_put_raises() -> None:
    """Test that WebToPdfHttp.put raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        web_to_pdf_http.put("some-endpoint/")


def test_web_to_pdf_patch_raises() -> None:
    """Test that WebToPdfHttp.patch raises NotImplementedError."""
    with pytest.raises(NotImplementedError):
        web_to_pdf_http.patch("some-endpoint/")
