"""Tests for the patient portal link client."""

from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import requests

from canvas_sdk.utils.http import ontologies_http, science_http
from canvas_sdk.utils.patient_portal import PatientPortalLinkError, patient_portal_http
from logger.logger import plugin_context


class FakePortalResponse:
    """A mock requests.Response carrying a minted portal link."""

    def __init__(self, status_code: int = 200, payload: Any = None) -> None:
        self.status_code = status_code
        self._payload = payload
        # A real response also carries the request, whose headers hold the pre-shared key.
        self.request = MagicMock()
        self.request.headers = {"Authorization": "the-pre-shared-key"}

    def json(self) -> Any:
        """Return the configured payload."""
        return self._payload


@patch("requests.Session.post")
def test_patient_portal_get_login_url(mock_post: MagicMock) -> None:
    """get_login_url posts the patient and link type, and returns the link."""
    mock_post.return_value = FakePortalResponse(
        payload={"login_url": "https://example.canvasmedical.com/app/reset/?access_token=abc"}
    )

    login_url = patient_portal_http.get_login_url("a" * 32, link_type="reset")

    assert login_url == "https://example.canvasmedical.com/app/reset/?access_token=abc"

    _, kwargs = mock_post.call_args

    assert kwargs["json"] == {
        "patient_id": "a" * 32,
        "link_type": "reset",
        "next_path": "/",
    }


@patch("requests.Session.post")
def test_patient_portal_defaults_to_an_invite(mock_post: MagicMock) -> None:
    """The default link type is an invite, and ttl is omitted unless asked for."""
    mock_post.return_value = FakePortalResponse(payload={"login_url": "https://x/app/reset/"})

    patient_portal_http.get_login_url("b" * 32)

    _, kwargs = mock_post.call_args

    assert kwargs["json"]["link_type"] == "invite"
    assert "ttl" not in kwargs["json"]


@patch("requests.Session.post")
def test_patient_portal_passes_ttl_and_next_path(mock_post: MagicMock) -> None:
    """Both ttl and next_path reach the endpoint when supplied."""
    mock_post.return_value = FakePortalResponse(payload={"login_url": "https://x/app/reset/"})

    patient_portal_http.get_login_url("c" * 32, next_path="/messages/", ttl=600)

    _, kwargs = mock_post.call_args

    assert kwargs["json"]["next_path"] == "/messages/"
    assert kwargs["json"]["ttl"] == 600


@patch("requests.Session.post")
def test_patient_portal_posts_to_canvas(mock_post: MagicMock) -> None:
    """The request goes to the portal-link endpoint on Canvas itself."""
    mock_post.return_value = FakePortalResponse(payload={"login_url": "https://x/app/reset/"})

    patient_portal_http.get_login_url("d" * 32)

    call_url = mock_post.call_args[0][0]

    assert call_url.endswith("/patient-portal/login-url/")


@patch("requests.Session.post")
def test_patient_portal_names_the_active_plugin(mock_post: MagicMock) -> None:
    """The active plugin is named for the audit trail."""
    mock_post.return_value = FakePortalResponse(payload={"login_url": "https://x/app/reset/"})

    with plugin_context("ringcentral_softphone.handlers.invite.SendInvite"):
        patient_portal_http.get_login_url("e" * 32)

    _, kwargs = mock_post.call_args

    assert kwargs["headers"] == {"X-Canvas-Plugin-Name": "ringcentral_softphone"}


@patch("requests.Session.post")
def test_patient_portal_sends_no_plugin_header_outside_a_handler(mock_post: MagicMock) -> None:
    """Outside a handler there is no plugin to name."""
    mock_post.return_value = FakePortalResponse(payload={"login_url": "https://x/app/reset/"})

    patient_portal_http.get_login_url("f" * 32)

    _, kwargs = mock_post.call_args

    assert kwargs["headers"] is None


@patch("requests.Session.post")
def test_patient_portal_hides_the_pre_shared_key(mock_post: MagicMock) -> None:
    """Plugin code must not be able to read the injected key back off the response.

    JsonOnlyResponse exposes only status_code and json(), and the sandbox blocks the
    underscored client, so there is no route from plugin code to the key.
    """
    mock_post.return_value = FakePortalResponse(payload={"login_url": "https://x/app/reset/"})

    patient_portal_http.get_login_url("a" * 32)

    response = patient_portal_http._http_client.post_json("/patient-portal/login-url/", json={})

    assert not hasattr(response, "request")
    assert not hasattr(response, "headers")
    assert set(vars(response)) == {"_json", "status_code"}


@patch("requests.Session.post")
def test_patient_portal_raises_on_an_error_status(mock_post: MagicMock) -> None:
    """A non-200 is an error the plugin author should see, not an empty string."""
    mock_post.return_value = FakePortalResponse(status_code=404, payload={"error": "not found"})

    with pytest.raises(PatientPortalLinkError) as excinfo:
        patient_portal_http.get_login_url("0" * 32)

    assert excinfo.value.status_code == 404


@patch("requests.Session.post")
def test_patient_portal_raises_when_no_link_comes_back(mock_post: MagicMock) -> None:
    """A 200 carrying no link is still a failure."""
    mock_post.return_value = FakePortalResponse(payload={})

    with pytest.raises(PatientPortalLinkError, match="carried no link"):
        patient_portal_http.get_login_url("a" * 32)


@patch("requests.Session.post")
def test_patient_portal_raises_when_the_body_is_not_json(mock_post: MagicMock) -> None:
    """An HTML error page decodes to no JSON at all."""
    mock_post.return_value = FakePortalResponse(payload=None)

    with pytest.raises(PatientPortalLinkError, match="carried no link"):
        patient_portal_http.get_login_url("a" * 32)


@patch("requests.Session.post")
def test_patient_portal_wraps_a_transport_failure(mock_post: MagicMock) -> None:
    """A timeout or DNS failure is uncatchable from a plugin unless it is re-raised.

    `requests` is not in the sandbox's allowed imports, so a plugin author cannot name
    `requests.exceptions.Timeout`.
    """
    mock_post.side_effect = requests.exceptions.ConnectTimeout("no route")

    with pytest.raises(PatientPortalLinkError) as excinfo:
        patient_portal_http.get_login_url("a" * 32)

    assert excinfo.value.status_code == 0
    assert "Could not reach Canvas" in excinfo.value.message


@patch("requests.Session.post")
def test_patient_portal_raises_when_the_body_is_not_an_object(mock_post: MagicMock) -> None:
    """A 200 whose body decodes to something other than an object is still a failure."""
    mock_post.return_value = FakePortalResponse(payload=["not", "an", "object"])

    with pytest.raises(PatientPortalLinkError, match="carried no link"):
        patient_portal_http.get_login_url("a" * 32)


@patch("requests.Session.post")
def test_patient_portal_raises_when_the_link_is_not_a_string(mock_post: MagicMock) -> None:
    """A non-string link is a failure rather than something coerced with str()."""
    mock_post.return_value = FakePortalResponse(payload={"login_url": 123})

    with pytest.raises(PatientPortalLinkError, match="carried no link"):
        patient_portal_http.get_login_url("a" * 32)


def test_post_is_not_added_to_the_shared_json_only_base() -> None:
    """The POST primitive must not reach the clients plugin code holds directly.

    `ontologies_http` and `science_http` are exported to the sandbox and were GET-only.
    """
    assert not hasattr(ontologies_http, "post_json")
    assert not hasattr(science_http, "post_json")
