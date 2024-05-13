from unittest.mock import MagicMock, patch

from canvas_sdk.utils import Http


@patch("requests.Session.get")
def test_http_get(mock_get: MagicMock) -> None:
    http = Http()
    http.get("https://www.canvasmedical.com/", headers={"Authorization": "Bearer as;ldkfjdkj"})
    mock_get.assert_called_once_with(
        "https://www.canvasmedical.com/", headers={"Authorization": "Bearer as;ldkfjdkj"}
    )


@patch("requests.Session.post")
def test_http_post(mock_post: MagicMock) -> None:
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
    )


@patch("requests.Session.put")
def test_http_put(mock_put: MagicMock) -> None:
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
    )


@patch("requests.Session.patch")
def test_http_patch(mock_patch: MagicMock) -> None:
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
    )
