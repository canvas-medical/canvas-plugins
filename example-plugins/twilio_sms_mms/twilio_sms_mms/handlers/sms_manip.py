from http import HTTPStatus

from canvas_sdk.clients.twilio.constants import DateOperation, HttpMethod
from canvas_sdk.clients.twilio.libraries import SmsClient
from canvas_sdk.clients.twilio.structures import (
    RequestFailed,
    Settings,
    SmsMms,
    StatusInbound,
    StatusOutboundApi,
)
from canvas_sdk.effects import Effect
from canvas_sdk.effects.simple_api import HTMLResponse, JSONResponse, Response
from canvas_sdk.handlers.simple_api import Credentials, SimpleAPI, api
from logger import log

from ..constants.constants import Constants


class SmsManip(SimpleAPI):
    """API handler for Twilio SMS/MMS operations.

    This class provides REST API endpoints for managing Twilio SMS/MMS functionality,
    including sending messages, retrieving phone numbers, managing webhooks, and
    handling inbound/outbound message callbacks.
    """

    PREFIX = None

    def authenticate(self, credentials: Credentials) -> bool:
        """Authenticate API requests.

        Args:
            credentials: The credentials to authenticate.

        Returns:
            bool: Always returns True for simplicity. TODO: implement proper authentication.
        """
        return True

    def _twillio_client(self) -> SmsClient:
        """Create and configure a Twilio SMS client.

        Returns:
            SmsClient: Configured Twilio SMS client instance with credentials from secrets.
        """
        settings = Settings(
            account_sid=self.secrets[Constants.twillio_account_sid],
            key=self.secrets[Constants.twillio_api_key],
            secret=self.secrets[Constants.twillio_api_secret],
        )
        return SmsClient(settings)

    @api.get("/phone_list")
    def phone_list(self) -> list[Response | Effect]:
        """Retrieve the list of phone numbers associated with the Twilio account.

        Returns:
            list[Response | Effect]: JSON response containing a list of phone numbers with their
                properties (SID, phone number, label, capabilities, status, and inbound webhook configuration).
                Returns error information if the request fails.
        """
        client = self._twillio_client()
        try:
            result = [
                JSONResponse(
                    [
                        {
                            "sid": p.sid,
                            "phoneNumber": p.phone_number,
                            "label": p.friendly_name,
                            "capabilities": p.capabilities.to_dict(),
                            "statusCallback": p.status_callback,
                            "status": p.status,
                            "inboundWebhook": {
                                "url": p.sms_url,
                                "method": p.sms_method.value,
                            },
                        }
                        for p in client.account_phone_numbers()
                    ],
                    status_code=HTTPStatus(HTTPStatus.OK),
                ),
            ]
        except RequestFailed as e:
            result = [
                JSONResponse({"information": e.message}, status_code=HTTPStatus(e.status_code))
            ]
        return result

    @api.get("/message_list/<number>/<direction>")
    def message_list(self) -> list[Response | Effect]:
        """Retrieve a list of messages for a specific phone number.

        Path Parameters:
            number: The phone number to filter messages.
            direction: Message direction filter, either "from" or "to".

        Returns:
            list[Response | Effect]: JSON response containing a list of messages with their
                SID, sent timestamp, status, and media count. Returns error information if the request fails.
        """
        number = self.request.path_params["number"]
        direction = self.request.path_params["direction"]
        number_from = number if direction == "from" else ""
        number_to = number if direction == "to" else ""

        client = self._twillio_client()
        try:
            result = [
                JSONResponse(
                    [
                        {
                            "sid": p.sid,
                            "sent": p.date_sent.isoformat(),
                            "status": p.status.value,
                            "mediaCount": p.count_media,
                        }
                        for p in client.retrieve_all_sms(
                            number_to, number_from, "", DateOperation.ON_EXACTLY
                        )
                    ],
                    status_code=HTTPStatus(HTTPStatus.OK),
                ),
            ]
        except RequestFailed as e:
            result = [
                JSONResponse({"information": e.message}, status_code=HTTPStatus(e.status_code))
            ]
        return result

    @api.get("/message/<message_sid>")
    def message(self) -> list[Response | Effect]:
        """Retrieve details of a specific message.

        Path Parameters:
            message_sid: The SID of the message to retrieve.

        Returns:
            list[Response | Effect]: JSON response containing the full message details.
                Returns error information if the request fails.
        """
        message_sid = self.request.path_params["message_sid"]
        client = self._twillio_client()
        try:
            result = [
                JSONResponse(
                    client.retrieve_sms(message_sid).to_dict(),
                    status_code=HTTPStatus(HTTPStatus.OK),
                ),
            ]
        except RequestFailed as e:
            result = [
                JSONResponse({"information": e.message}, status_code=HTTPStatus(e.status_code))
            ]
        return result

    @api.get("/medias/<message_sid>")
    def media_list(self) -> list[Response | Effect]:
        """Retrieve all media attachments for a specific message.

        Path Parameters:
            message_sid: The SID of the message to retrieve media from.

        Returns:
            list[Response | Effect]: List of Response objects, each containing media content
                with its appropriate content type. Returns error information if the request fails.
        """
        message_sid = self.request.path_params["message_sid"]
        client = self._twillio_client()
        try:
            result = [
                Response(
                    content_type=p.content_type,
                    content=client.retrieve_raw_media(message_sid, p.sid),
                )
                for p in client.retrieve_media_list(message_sid)
            ]
        except RequestFailed as e:
            result = [
                JSONResponse({"information": e.message}, status_code=HTTPStatus(e.status_code))
            ]
        return result

    @api.delete("/message_delete/<message_sid>")
    def message_delete(self) -> list[Response | Effect]:
        """Delete a specific message from Twilio.

        Path Parameters:
            message_sid: The SID of the message to delete.

        Returns:
            list[Response | Effect]: JSON response containing the message SID and deletion status.
                Returns error information if the request fails.
        """
        message_sid = self.request.path_params["message_sid"]
        client = self._twillio_client()
        try:
            result = [
                JSONResponse(
                    {
                        "sid": message_sid,
                        "deleted": client.delete_sms(message_sid),
                    },
                    status_code=HTTPStatus(HTTPStatus.OK),
                )
            ]
        except RequestFailed as e:
            result = [
                JSONResponse({"information": e.message}, status_code=HTTPStatus(e.status_code))
            ]
        return result

    @api.post("/inbound_webhook/<phone_sid>")
    def inbound_webhook(self) -> list[Response | Effect]:
        """Configure the inbound webhook URL for a Twilio phone number.

        Path Parameters:
            phone_sid: The SID of the phone number to configure.

        Request Body:
            url: The webhook URL to set for inbound messages.
            method: The HTTP method for the webhook (GET or POST).

        Returns:
            list[Response | Effect]: JSON response containing the configuration result.
                Returns error information if the request fails.
        """
        phone_sid = self.request.path_params["phone_sid"]
        content = self.request.json()
        webhook_url = content["url"]
        method = HttpMethod(content["method"])

        client = self._twillio_client()
        try:
            response = client.set_inbound_webhook(phone_sid, webhook_url, method)
            result = [JSONResponse({"result": response}, status_code=HTTPStatus(HTTPStatus.OK))]
        except RequestFailed as e:
            result = [
                JSONResponse({"information": e.message}, status_code=HTTPStatus(e.status_code))
            ]
        return result

    @api.post("/sms_send")
    def sms_send(self) -> list[Response | Effect]:
        """Send an SMS message via Twilio.

        Request Body:
            numberFrom: The phone number to send from (optional if numberFromSid is provided).
            numberFromSid: The SID of the phone number to send from (optional if numberFrom is provided).
            numberTo: The destination phone number.
            callbackUrl: Optional URL for status callbacks.
            text: The message text to send.

        Returns:
            list[Response | Effect]: JSON response containing the sent message details.
                Returns error information if the request fails.
        """
        content = self.request.json()
        number_from = content.get("numberFrom")
        number_from_id = content.get("numberFromSid")
        number_to = content.get("numberTo")
        callback_url = content.get("callbackUrl")
        text = content.get("text")

        client = self._twillio_client()
        try:
            sms_mms = SmsMms(
                number_from=number_from,
                number_from_sid=number_from_id,
                number_to=number_to,
                message=text,
                media_url="",
                status_callback_url=callback_url,
            )
            response = client.send_sms_mms(sms_mms)
            result = [JSONResponse(response.to_dict(), status_code=HTTPStatus(HTTPStatus.OK))]
        except RequestFailed as e:
            result = [
                JSONResponse({"information": e.message}, status_code=HTTPStatus(e.status_code))
            ]
        return result

    @api.post("/outbound_api_status")
    def outbound_api_status(self) -> list[Response | Effect]:
        """Handle status callbacks for outbound SMS messages.

        This endpoint receives status updates from Twilio for messages that were sent
        through the API, logging the message SID and status.

        Returns:
            list[Response | Effect]: Empty response with 200 OK status.
        """
        status = StatusOutboundApi.callback_outbound_api(self.request.text())
        log.info(f"sms_extern: sid/status: {status.sms_sid}/{status.sms_status}")
        return [Response(status_code=HTTPStatus(HTTPStatus.OK))]

    @api.post("/inbound_treatment")
    def inbound_treatment(self) -> list[Response | Effect]:
        """Handle inbound SMS messages with automatic replies.

        This endpoint processes incoming messages and generates automatic responses.
        If the message contains "hello", it replies with a greeting and an image.
        Otherwise, it prompts the user to say hello.

        Returns:
            list[Response | Effect]: HTML response containing TwiML with the reply message
                and optional media attachment.
        """
        inbound = StatusInbound.callback_inbound(self.request.text())
        if "hello" in inbound.body.lower():
            reply = "Hello! ♥️"
            image = "<Media>https://img.freepik.com/free-psd/hand-drawn-summer-frame-illustration_23-2151631028.jpg</Media>"
        else:
            reply = "Say hello! 👻"
            image = ""

        response = (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<Response>"
            f"<Message><Body>{reply}</Body>{image}</Message>"
            "</Response>"
        )
        return [
            HTMLResponse(
                content=response,
                status_code=HTTPStatus(HTTPStatus.OK),
            )
        ]
