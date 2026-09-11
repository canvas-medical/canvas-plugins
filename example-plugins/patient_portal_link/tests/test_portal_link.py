"""Tests for the patient_portal_link example plugin."""

from unittest.mock import Mock, patch

from patient_portal_link.routes.portal_link import SendPortalLinkAPI

from canvas_sdk.effects.simple_api import JSONResponse
from canvas_sdk.utils.patient_portal import PatientPortalLinkError
from canvas_sdk.v1.data import Patient

PATIENT_ID = "a" * 32
LOGIN_URL = "https://example.canvasmedical.com/app/reset/?access_token=abc&next=%2F"


class DummyRequest:
    """A dummy request object carrying a JSON body."""

    def __init__(self, json_body: dict[str, object] | None = None) -> None:
        self._json_body = json_body or {}

    def json(self) -> dict[str, object]:
        """Return the mocked JSON body."""
        return self._json_body


class DummyEvent:
    """A dummy event object for testing API handlers."""

    def __init__(self, context: dict[str, object] | None = None) -> None:
        self.context = context or {}


def build_api(json_body: dict[str, object] | None = None) -> SendPortalLinkAPI:
    """An API instance wired with secrets and a request body."""
    api = SendPortalLinkAPI(event=DummyEvent(context={"method": "POST", "path": "/send"}))
    api.secrets = {
        "my-api-key": "valid-secret-key",
        "sms-provider-url": "https://provider.example.com/messages",
        "sms-provider-token": "provider-token",
    }
    api.request = DummyRequest(json_body)

    return api


def patient_mock(is_portal_registered: bool) -> Mock:
    """A patient whose user has the given registration state."""
    patient = Mock(spec=Patient)
    patient.id = PATIENT_ID
    patient.user = Mock()
    patient.user.is_portal_registered = is_portal_registered
    patient.user.phone_number = "+15551234567"

    return patient


def test_path_is_configured() -> None:
    """The route is mounted where the README says it is."""
    assert SendPortalLinkAPI.PATH == "/send"


def test_authenticate_with_a_valid_key() -> None:
    """Authentication succeeds with the configured API key."""
    api = build_api({"patient_id": PATIENT_ID})
    credentials = Mock()
    credentials.key = "valid-secret-key"

    assert api.authenticate(credentials) is True


def test_authenticate_with_an_invalid_key() -> None:
    """Authentication fails with any other key."""
    api = build_api({"patient_id": PATIENT_ID})
    credentials = Mock()
    credentials.key = "wrong-key"

    assert api.authenticate(credentials) is False


def test_mints_an_invite_for_an_unregistered_patient() -> None:
    """An unregistered patient gets the activation copy."""
    api = build_api({"patient_id": PATIENT_ID})

    with (
        patch.object(Patient.objects, "filter") as mock_filter,
        patch(
            "patient_portal_link.routes.portal_link.patient_portal_http.get_login_url",
            return_value=LOGIN_URL,
        ) as mock_get_login_url,
        patch.object(SendPortalLinkAPI, "deliver") as mock_deliver,
    ):
        mock_filter.return_value.first.return_value = patient_mock(is_portal_registered=False)

        result = api.post()

    mock_get_login_url.assert_called_once_with(PATIENT_ID, link_type="invite")
    assert "activate your password" in mock_deliver.call_args.kwargs["message"]
    assert LOGIN_URL in mock_deliver.call_args.kwargs["message"]
    assert isinstance(result[0], JSONResponse)


def test_mints_a_reset_for_a_registered_patient() -> None:
    """A registered patient gets the reset copy."""
    api = build_api({"patient_id": PATIENT_ID})

    with (
        patch.object(Patient.objects, "filter") as mock_filter,
        patch(
            "patient_portal_link.routes.portal_link.patient_portal_http.get_login_url",
            return_value=LOGIN_URL,
        ) as mock_get_login_url,
        patch.object(SendPortalLinkAPI, "deliver") as mock_deliver,
    ):
        mock_filter.return_value.first.return_value = patient_mock(is_portal_registered=True)

        api.post()

    mock_get_login_url.assert_called_once_with(PATIENT_ID, link_type="reset")
    assert "reset your account" in mock_deliver.call_args.kwargs["message"]


def test_requires_a_patient_id() -> None:
    """A body with no patient_id is a 400."""
    api = build_api({})

    result = api.post()

    assert result[0].status_code == 400


def test_reports_an_unknown_patient() -> None:
    """A patient_id that matches nothing is a 404."""
    api = build_api({"patient_id": PATIENT_ID})

    with patch.object(Patient.objects, "filter") as mock_filter:
        mock_filter.return_value.first.return_value = None

        result = api.post()

    assert result[0].status_code == 404


def test_reports_a_failed_mint() -> None:
    """A mint failure is a 502, not a message with a broken link in it."""
    api = build_api({"patient_id": PATIENT_ID})

    with (
        patch.object(Patient.objects, "filter") as mock_filter,
        patch(
            "patient_portal_link.routes.portal_link.patient_portal_http.get_login_url",
            side_effect=PatientPortalLinkError(502, "nope"),
        ),
        patch.object(SendPortalLinkAPI, "deliver") as mock_deliver,
    ):
        mock_filter.return_value.first.return_value = patient_mock(is_portal_registered=False)

        result = api.post()

    assert result[0].status_code == 502
    mock_deliver.assert_not_called()


def test_reports_a_patient_with_no_portal_user() -> None:
    """`Patient.user` is nullable, so a patient with no portal account is a 400."""
    api = build_api({"patient_id": PATIENT_ID})
    patient = Mock(spec=Patient)
    patient.id = PATIENT_ID
    patient.user = None

    with patch.object(Patient.objects, "filter") as mock_filter:
        mock_filter.return_value.first.return_value = patient

        result = api.post()

    assert result[0].status_code == 400


def test_reports_a_patient_with_no_phone_number() -> None:
    """There is nowhere to deliver a link for a patient with no number on file."""
    api = build_api({"patient_id": PATIENT_ID})
    patient = patient_mock(is_portal_registered=False)
    patient.user.phone_number = ""

    with patch.object(Patient.objects, "filter") as mock_filter:
        mock_filter.return_value.first.return_value = patient

        result = api.post()

    assert result[0].status_code == 400


def test_reports_a_failed_delivery() -> None:
    """A minted link the provider rejected must not be reported as sent."""
    api = build_api({"patient_id": PATIENT_ID})

    with (
        patch.object(Patient.objects, "filter") as mock_filter,
        patch(
            "patient_portal_link.routes.portal_link.patient_portal_http.get_login_url",
            return_value=LOGIN_URL,
        ),
        patch.object(SendPortalLinkAPI, "deliver", return_value=False),
    ):
        mock_filter.return_value.first.return_value = patient_mock(is_portal_registered=False)

        result = api.post()

    assert result[0].status_code == 502


def test_deliver_reports_the_provider_status() -> None:
    """`deliver` reports success from the provider response rather than assuming it."""
    api = build_api({"patient_id": PATIENT_ID})

    with patch("patient_portal_link.routes.portal_link.Http.post") as mock_post:
        mock_post.return_value = Mock(status_code=200)
        assert api.deliver(to="+15551234567", message="hi") is True

        mock_post.return_value = Mock(status_code=401)
        assert api.deliver(to="+15551234567", message="hi") is False
