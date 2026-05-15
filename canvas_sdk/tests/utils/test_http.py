import logging
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from canvas_sdk.utils import Http
from canvas_sdk.utils.http import ontologies_http, pharmacy_http, science_http


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
        "https://pharmacy-2017071.canvasmedical.com/surescripts/pharmacy/",
        headers={},
        timeout=30,
    )

    pharmacy_http.search_pharmacies("abc123")

    mock_get.assert_called_with(
        "https://pharmacy-2017071.canvasmedical.com/surescripts/pharmacy/?search=abc123",
        headers={},
        timeout=30,
    )


@patch("requests.Session.get")
def test_search_pharmacies_with_filter_fields(mock_get: MagicMock) -> None:
    """Test that search_pharmacies passes filter fields as query parameters."""
    mock_get.return_value = FakeResponse()

    pharmacy_http.search_pharmacies(
        search_term=None,
        ncpdp_id="1234567",
        organization_name="CVS",
        state="CA",
        zip_code_prefix="902",
        specialty_type="retail",
    )

    call_url = mock_get.call_args[0][0]
    assert "ncpdp_id=1234567" in call_url
    assert "organization_name__icontains=CVS" in call_url
    assert "state__iexact=CA" in call_url
    assert "zip_code_prefix_in=902" in call_url
    assert "specialty_type__icontains=retail" in call_url
    assert "search=" not in call_url


@patch("requests.Session.get")
def test_search_pharmacies_with_id(mock_get: MagicMock) -> None:
    """Test that search_pharmacies passes an exact id filter."""
    mock_get.return_value = FakeResponse()

    pharmacy_http.search_pharmacies(search_term=None, id=42)

    call_url = mock_get.call_args[0][0]
    assert "id=42" in call_url


@patch("requests.Session.get")
def test_search_pharmacies_with_zip_code_prefix(mock_get: MagicMock) -> None:
    """Test that search_pharmacies passes zip_code_prefix."""
    mock_get.return_value = FakeResponse()

    pharmacy_http.search_pharmacies(search_term=None, zip_code_prefix="902,100,945")

    call_url = mock_get.call_args[0][0]
    assert "zip_code_prefix_in=902%2C100%2C945" in call_url


@patch("requests.Session.get")
def test_search_pharmacies_with_location(mock_get: MagicMock) -> None:
    """Test that latitude and longitude are passed when provided."""
    mock_get.return_value = FakeResponse()

    pharmacy_http.search_pharmacies("walgreens", latitude="34.05", longitude="-118.24")

    call_url = mock_get.call_args[0][0]
    assert "search=walgreens" in call_url
    assert "latitude=34.05" in call_url
    assert "longitude=-118.24" in call_url


@pytest.mark.parametrize(
    "client",
    [
        pytest.param(ontologies_http, id="ontologies_http"),
        pytest.param(science_http, id="science_http"),
    ],
)
def test_overriding_max_timeout_logs_deprecation_warning(
    client: Http,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Overriding _MAX_REQUEST_TIMEOUT_SECONDS should still work but log a deprecation warning."""
    original = type(client)._MAX_REQUEST_TIMEOUT_SECONDS

    with caplog.at_level(logging.WARNING, logger="plugin_runner_logger"):
        client._MAX_REQUEST_TIMEOUT_SECONDS = 120

    assert "deprecated" in caplog.text.lower()
    assert type(client).__name__ in caplog.text

    # The override should have taken effect
    assert client._MAX_REQUEST_TIMEOUT_SECONDS == 120

    # Clean up: remove instance override to restore class default
    del client._MAX_REQUEST_TIMEOUT_SECONDS
    assert original == client._MAX_REQUEST_TIMEOUT_SECONDS
