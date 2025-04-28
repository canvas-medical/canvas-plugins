from typing import Any
from unittest.mock import MagicMock, patch

from canvas_sdk.utils import Http
from canvas_sdk.utils.http import ontologies_http


class FakeResponse:
    """
    A mock requests.Response.
    """

    def __init__(self) -> None:
        self.status_code = 200

    def json(self) -> dict[str, Any]:
        """
        Return a known response for mocking.
        """
        return {"abc": 123}


@patch("requests.Session.get")
def test_http_get_json(mock_get: MagicMock) -> None:
    """Test that the Http.get method calls requests.get with the correct arguments."""
    mock_get.return_value = FakeResponse()

    response = ontologies_http.get_json("/fdb/medication")

    mock_get.assert_called_once_with(
        "https://ontologies.canvasmedical.com/fdb/medication",
        headers={},
        timeout=30,
    )

    assert response.status_code == 200
    assert response.json() == {"abc": 123}


@patch("requests.Session.get")
def test_http_get(mock_get: MagicMock) -> None:
    """Test that the Http.get method calls requests.get with the correct arguments."""
    http = Http()
    http.get("https://www.canvasmedical.com/", headers={"Authorization": "Bearer as;ldkfjdkj"})
    mock_get.assert_called_once_with(
        "https://www.canvasmedical.com/",
        headers={"Authorization": "Bearer as;ldkfjdkj"},
        timeout=30,
    )


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
