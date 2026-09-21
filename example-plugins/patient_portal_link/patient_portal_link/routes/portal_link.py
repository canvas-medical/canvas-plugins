from http import HTTPStatus

from canvas_sdk.effects.simple_api import JSONResponse, Response
from canvas_sdk.handlers.simple_api import APIKeyCredentials, SimpleAPIRoute
from canvas_sdk.utils import Http
from canvas_sdk.utils.patient_portal import PatientPortalLinkError, patient_portal_http
from canvas_sdk.v1.data import Patient
from logger import log

# POST /plugin-io/api/patient_portal_link/send
# Headers: "Authorization: <your value for 'my-api-key'>"
# Body: {"patient_id": "<32-character patient id>"}


class SendPortalLinkAPI(SimpleAPIRoute):
    """Mint a patient's portal link and deliver it over our own transport.

    Canvas's own invite goes out over Canvas's Twilio and SendGrid. This mints the same link
    and hands it to whatever provider this plugin is configured with, so the message reaches
    the patient from the practice's own number or address.
    """

    PATH = "/send"

    def authenticate(self, credentials: APIKeyCredentials) -> bool:
        """Simple API key authentication."""
        return credentials.key == self.secrets["my-api-key"]

    def post(self) -> list[Response]:
        """Mint a portal link for the requested patient and send it."""
        patient_id = (self.request.json() or {}).get("patient_id")

        if not patient_id:
            return [
                JSONResponse(
                    {"error": "patient_id is required"}, status_code=HTTPStatus.BAD_REQUEST
                )
            ]

        patient = Patient.objects.filter(id=patient_id).first()

        if not patient:
            return [JSONResponse({"error": "patient not found"}, status_code=HTTPStatus.NOT_FOUND)]

        # `Patient.user` is nullable: a patient with no portal account has nobody to send to.
        if not patient.user or not patient.user.phone_number:
            return [
                JSONResponse(
                    {"error": "patient has no phone number on file"},
                    status_code=HTTPStatus.BAD_REQUEST,
                )
            ]

        # A first invite and a password reset are the same link. Which one this is depends on
        # whether the patient has finished registering, which is also what decides the copy.
        registered = patient.user.is_portal_registered
        link_type = "reset" if registered else "invite"

        try:
            login_url = patient_portal_http.get_login_url(patient_id, link_type=link_type)
        except PatientPortalLinkError:
            log.exception("Could not mint a portal link")

            return [
                JSONResponse(
                    {"error": "could not mint a portal link"}, status_code=HTTPStatus.BAD_GATEWAY
                )
            ]

        message = (
            f"Click here to reset your account: {login_url}"
            if registered
            else f"Click here to activate your password: {login_url}"
        )

        if not self.deliver(to=patient.user.phone_number, message=message):
            # A link was minted and never reached the patient. Saying so beats reporting a
            # send that did not happen.
            return [
                JSONResponse(
                    {"error": "could not deliver the link"}, status_code=HTTPStatus.BAD_GATEWAY
                )
            ]

        return [JSONResponse({"sent": True, "link_type": link_type})]

    def deliver(self, to: str, message: str) -> bool:
        """Send the message over this practice's own provider.

        Stands in for a real provider call. Swap the URL and payload for RingCentral, a
        customer-owned Twilio account, or anything else that speaks HTTP; `Http` is the SDK's
        general-purpose outbound client.
        """
        http = Http()

        response = http.post(
            self.secrets["sms-provider-url"],
            json={"to": to, "body": message},
            headers={"Authorization": f"Bearer {self.secrets['sms-provider-token']}"},
        )

        return response.status_code < 400
