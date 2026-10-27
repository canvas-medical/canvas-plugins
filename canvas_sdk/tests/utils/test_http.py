import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests
from cryptography import x509
from cryptography.x509.oid import NameOID

from canvas_sdk.utils import Http
from canvas_sdk.utils.http import (
    SURESCRIPTS_CA_BUNDLE,
    JsonOnlyResponse,
    ServiceClient,
    _SurescriptsTrustAdapter,
    ontologies_http,
    pharmacy_http,
    science_http,
)


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
    client: Any,
    caplog: pytest.LogCaptureFixture,
) -> None:
    """Overriding _MAX_REQUEST_TIMEOUT_SECONDS should still work but log a deprecation warning."""
    original = client._MAX_REQUEST_TIMEOUT_SECONDS

    with caplog.at_level(logging.WARNING, logger="plugin_runner_logger"):
        client._MAX_REQUEST_TIMEOUT_SECONDS = 120

    assert "deprecated" in caplog.text.lower()
    assert type(client).__name__ in caplog.text

    # The override should have taken effect
    assert client._MAX_REQUEST_TIMEOUT_SECONDS == 120

    # Clean up: remove instance override to restore class default
    del client._MAX_REQUEST_TIMEOUT_SECONDS
    assert original == client._MAX_REQUEST_TIMEOUT_SECONDS


@pytest.mark.parametrize(
    "url",
    [
        pytest.param("https://api.example.com.other.example/x", id="host_suffix"),
        pytest.param("https://api.example.com@other.example/x", id="userinfo"),
        pytest.param("https://user:pw@api.example.com/x", id="userinfo_same_host"),
        pytest.param("//other.example/x", id="scheme_relative"),
        pytest.param("http://api.example.com/x", id="other_scheme"),
        pytest.param("https://api.example.com:8443/x", id="other_port"),
        pytest.param("https://api.example.com/v1x/y", id="sibling_of_base_path"),
    ],
)
def test_join_url_rejects_urls_outside_the_base(url: str) -> None:
    """A URL is inside the base only if scheme, host, port and path prefix all match."""
    http = Http(base_url="https://api.example.com/v1")

    with pytest.raises(ValueError):
        http.join_url(url)


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        pytest.param("/v1/thing", "https://api.example.com/v1/thing", id="absolute_path"),
        pytest.param("thing", "https://api.example.com/v1/thing", id="relative_path"),
        pytest.param(
            "https://api.example.com/v1/thing?q=1",
            "https://api.example.com/v1/thing?q=1",
            id="same_origin_url",
        ),
        pytest.param(
            "https://api.example.com:443/v1/thing",
            "https://api.example.com:443/v1/thing",
            id="explicit_default_port",
        ),
    ],
)
def test_join_url_accepts_urls_inside_the_base(url: str, expected: str) -> None:
    """URLs under the base resolve as before."""
    http = Http(base_url="https://api.example.com/v1/")

    assert http.join_url(url) == expected


def test_join_url_without_a_base_accepts_any_url() -> None:
    """A plugin's own client with no base URL can reach any host."""
    assert Http().join_url("https://anywhere.example/x") == "https://anywhere.example/x"


@pytest.mark.parametrize(
    "client",
    [
        pytest.param(ontologies_http, id="ontologies_http"),
        pytest.param(science_http, id="science_http"),
    ],
)
@pytest.mark.parametrize(
    "url",
    [
        pytest.param("https://ontologies.canvasmedical.com.other.example/", id="host_suffix"),
        pytest.param("https://other.example/", id="other_host"),
        pytest.param("//other.example/", id="scheme_relative"),
        pytest.param("https://ontologies.canvasmedical.com/fdb/", id="absolute_same_host"),
        pytest.param("/fdb/../admin/", id="dot_segment"),
        pytest.param("/fdb/%2e%2e/admin/", id="encoded_dot_segment"),
        pytest.param("/fdb\\..\\admin/", id="backslash"),
    ],
)
@patch("requests.Session.get")
def test_service_clients_send_relative_paths_only(
    mock_get: MagicMock, client: Any, url: str
) -> None:
    """Service clients send requests only to plain paths on their own service."""
    with pytest.raises(ValueError):
        client.get_json(url)

    mock_get.assert_not_called()


@pytest.mark.parametrize(
    "client",
    [
        pytest.param(ontologies_http, id="ontologies_http"),
        pytest.param(science_http, id="science_http"),
        pytest.param(pharmacy_http, id="pharmacy_http"),
    ],
)
@pytest.mark.parametrize(
    "method",
    ["get", "post", "put", "patch", "delete", "batch_requests", "join_url"],
)
def test_service_clients_have_no_raw_request_methods(client: Any, method: str) -> None:
    """Service clients expose only their purpose-built methods."""
    assert not hasattr(client, method)


@pytest.mark.parametrize(
    "client",
    [
        pytest.param(ontologies_http, id="ontologies_http"),
        pytest.param(science_http, id="science_http"),
    ],
)
def test_unbound_http_methods_cannot_use_a_service_client(client: Any) -> None:
    """`Http.get(ontologies_http, ...)` finds no credentialed session to send with."""
    with patch("requests.Session.get") as mock_get, pytest.raises(AttributeError):
        Http.get(client, "/")

    mock_get.assert_not_called()


def _failing_request(*args: Any, **kwargs: Any) -> None:
    request = requests.Request("GET", "https://ontologies.canvasmedical.com/x").prepare()
    request.headers["Authorization"] = "test-credential"
    raise requests.Timeout("timed out", request=request)


@pytest.mark.parametrize(
    "call",
    [
        pytest.param(lambda: ontologies_http.get_json("/x"), id="ontologies_http"),
        pytest.param(lambda: science_http.get_json("/x"), id="science_http"),
        pytest.param(lambda: pharmacy_http.search_pharmacies("x"), id="pharmacy_search"),
        pytest.param(lambda: pharmacy_http.get_pharmacy_by_ncpdp_id("1234567"), id="pharmacy_id"),
    ],
)
@patch("requests.Session.get", side_effect=_failing_request)
def test_service_client_errors_are_plain_request_exceptions(
    _mock_get: MagicMock, call: Any
) -> None:
    """A failed request is re-raised as a plain RequestException, with nothing chained."""
    with pytest.raises(requests.RequestException) as excinfo:
        call()

    error = excinfo.value
    assert error.request is None
    assert error.response is None
    assert error.__cause__ is None
    assert error.__context__ is None
    assert "test-credential" not in str(error)


class _PostingClient(ServiceClient):
    """A bare service client, to test the POST helper the purpose-built clients share."""

    def __init__(self) -> None:
        super().__init__(base_url="https://service.example")


@patch("requests.Session.post")
def test_service_client_post_json_sends_the_body_and_headers(mock_post: MagicMock) -> None:
    """`_post_json` posts JSON to a path on the service and wraps the response."""
    mock_post.return_value = MagicMock(status_code=201, json=lambda: {"ok": True})

    response = _PostingClient()._post_json("/things/", {"a": 1}, headers={"X-Test": "1"})

    assert isinstance(response, JsonOnlyResponse)
    assert (response.status_code, response.json()) == (201, {"ok": True})
    assert mock_post.call_args.args[0] == "https://service.example/things/"
    assert mock_post.call_args.kwargs["json"] == {"a": 1}
    assert mock_post.call_args.kwargs["headers"] == {"X-Test": "1"}


@patch("requests.Session.post")
def test_service_client_post_json_sends_to_paths_only(mock_post: MagicMock) -> None:
    """`_post_json` refuses anything but a plain path, before sending."""
    with pytest.raises(ValueError):
        _PostingClient()._post_json("https://other.example/things/", {})

    mock_post.assert_not_called()


@patch("requests.Session.post")
def test_service_client_post_json_errors_are_plain_request_exceptions(
    mock_post: MagicMock,
) -> None:
    """A failed POST is re-raised as a plain RequestException, with nothing chained."""
    request = requests.Request("POST", "https://service.example/things/").prepare()
    request.headers["Authorization"] = "test-credential"
    mock_post.side_effect = requests.Timeout("timed out", request=request)

    with pytest.raises(requests.RequestException) as excinfo:
        _PostingClient()._post_json("/things/", {})

    error = excinfo.value
    assert error.request is None
    assert error.__cause__ is None
    assert error.__context__ is None


@pytest.mark.parametrize(
    "ncpdp_id",
    [
        pytest.param("../../prescription-messages/?patient=1", id="traversal"),
        pytest.param("1234567/../../x", id="digits_then_traversal"),
        pytest.param("123?x=1", id="query"),
        pytest.param("123#frag", id="fragment"),
        pytest.param("", id="empty"),
        pytest.param("..", id="dot_dot"),
    ],
)
@patch("requests.Session.get")
def test_get_pharmacy_by_ncpdp_id_rejects_non_digit_ids(mock_get: MagicMock, ncpdp_id: str) -> None:
    """An NCPDP ID is digits; anything else is no pharmacy, and nothing is sent."""
    assert pharmacy_http.get_pharmacy_by_ncpdp_id(ncpdp_id) is None

    mock_get.assert_not_called()


def _surescripts_ca_certificates() -> list[x509.Certificate]:
    return x509.load_pem_x509_certificates(Path(SURESCRIPTS_CA_BUNDLE).read_bytes())


def test_pharmacy_http_trusts_the_public_roots_and_the_surescripts_ca() -> None:
    """Production presents a Surescripts-issued certificate, staging a public one; both verify."""
    session = pharmacy_http._http_client._session
    adapter = session.get_adapter("https://pharmacy-2017071.canvasmedical.com/")
    assert isinstance(adapter, _SurescriptsTrustAdapter)
    trusted = {
        attribute.value
        for der in adapter.ssl_context.get_ca_certs(binary_form=True)
        for attribute in x509.load_der_x509_certificate(der).subject.get_attributes_for_oid(
            NameOID.COMMON_NAME
        )
    }

    assert session.verify is True
    assert "Surescripts Root Certification Authority" in trusted
    assert "ISRG Root X1" in trusted


def test_surescripts_ca_bundle_holds_the_pharmacy_service_chain() -> None:
    """The bundle carries the root and the subordinate CA that signs the pharmacy service."""
    common_names = {
        certificate.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
        for certificate in _surescripts_ca_certificates()
    }

    assert {
        "Surescripts Root Certification Authority",
        "Surescripts Subordinate CA - Region 1",
    } <= common_names


def test_surescripts_ca_bundle_is_not_near_expiry() -> None:
    """Fails six months before any bundled CA expires, while there is time to replace it."""
    soonest = min(certificate.not_valid_after_utc for certificate in _surescripts_ca_certificates())

    assert soonest - datetime.now(UTC) > timedelta(days=180), (
        f"A Surescripts CA in {SURESCRIPTS_CA_BUNDLE} expires {soonest:%Y-%m-%d}; replace the "
        "bundle with the pharmacy service's current SURESCRIPTS_CERTIFICATE_CA."
    )


@patch("requests.Session.get")
def test_get_pharmacy_by_ncpdp_id(mock_get: MagicMock) -> None:
    """A digit ID is looked up at its own path."""
    mock_get.return_value = FakeResponse()

    assert pharmacy_http.get_pharmacy_by_ncpdp_id("1234567") == {"abc": 123}

    assert mock_get.call_args.args[0] == (
        "https://pharmacy-2017071.canvasmedical.com/surescripts/pharmacy/ncpdp_id/1234567/"
    )
