from base64 import b64encode
from collections.abc import Iterator
from http import HTTPStatus
from typing import TypeVar
from urllib.parse import urlencode

from canvas_sdk.clients.twillio.constants.date_operation import DateOperation
from canvas_sdk.clients.twillio.structures import Phone
from canvas_sdk.clients.twillio.structures.media import Media
from canvas_sdk.clients.twillio.structures.message import Message
from canvas_sdk.clients.twillio.structures.request_failed import RequestFailed
from canvas_sdk.clients.twillio.structures.settings import Settings
from canvas_sdk.clients.twillio.structures.sms_mms import SmsMms
from canvas_sdk.clients.twillio.structures.structure import Structure
from canvas_sdk.utils import Http

Data = TypeVar("Data", bound=Structure)


class SmsClient:
    """Twilio API client for sending and retrieving SMS messages.

    Provides methods to interact with Twilio's messaging API including
    sending messages, retrieving message details, and handling callbacks.
    """

    def __init__(self, settings: Settings):
        """Initialize the Twilio client with authentication settings.

        Args:
            settings: Twilio account settings containing credentials.
        """
        self.settings = settings
        self.http = Http(f"https://api.twilio.com/2010-04-01/Accounts/{self.settings.account_sid}/")

    def _auth_header(self) -> dict:
        """Generate Basic authentication header for Twilio API requests.

        Returns:
            Dictionary containing the Authorization header with base64 encoded credentials.
        """
        auth_header = b64encode(f"{self.settings.key}:{self.settings.secret}".encode()).decode()
        return {
            "Authorization": f"Basic {auth_header}",
        }

    def _valid_content_list(self, url: str, key: str, returned: type[Data]) -> Iterator[Data]:
        """Fetch paginated list data from Twilio API.

        Args:
            url: The API endpoint URL to fetch from.
            key: The JSON key containing the list of items.
            returned: The Structure type to deserialize items into.

        Yields:
            Instances of the specified Structure type.

        Raises:
            RequestFailed: If any API request fails.
        """
        while True:
            request = self.http.get(url, headers=self._auth_header())
            if request.status_code != HTTPStatus.OK:
                raise RequestFailed(request.status_code, request.content.decode())
            response = request.json()
            for item in response[key]:
                yield returned.from_dict(item)
            url = response.get("next_page_uri")
            if not url:
                break

    def account_phone_numbers(self) -> Iterator[Phone]:
        """Retrieve all phone numbers associated with the Twilio account.

        Yields:
            Phone instances for each phone number in the account.

        Raises:
            RequestFailed: If the API request fails.
        """
        url = "IncomingPhoneNumbers.json"
        yield from self._valid_content_list(url, "incoming_phone_numbers", Phone)

    def account_phone_number(self, phone_sid: str) -> Phone:
        """Retrieve details for a specific phone number by its SID.

        Args:
            phone_sid: The Twilio SID of the phone number.

        Returns:
            Phone instance with the phone number details.

        Raises:
            RequestFailed: If the API request fails.
        """
        url = f"IncomingPhoneNumbers/{phone_sid}.json"
        request = self.http.get(url, headers=self._auth_header())
        if request.status_code != HTTPStatus.OK:
            raise RequestFailed(request.status_code, request.content.decode())
        return Phone.from_dict(request.json())

    def send_sms_mms(self, sms_mms: SmsMms) -> Message:
        """Send an SMS or MMS message via Twilio.

        Args:
            sms_mms: The message details to send.

        Returns:
            Message instance with the created message details.

        Raises:
            RequestFailed: If the API request fails or phone lacks required capabilities.
        """
        url = "Messages.json"
        phone = self.account_phone_number(sms_mms.number_from_sid)  # maybe to be cached?
        data = sms_mms.to_api(phone.capabilities)
        headers = {"Content-Type": "application/x-www-form-urlencoded"} | self._auth_header()
        request = self.http.post(url, data=data, headers=headers)
        if request.status_code != HTTPStatus.CREATED:
            raise RequestFailed(request.status_code, request.content.decode())
        return Message.from_dict(request.json())

    def retrieve_sms(self, message_id: str) -> Message:
        """Retrieve details for a specific SMS message by its ID.

        Args:
            message_id: The Twilio message SID to retrieve.

        Returns:
            Message instance with the message details.

        Raises:
            RequestFailed: If the API request fails.
        """
        url = f"Messages/{message_id}.json"
        request = self.http.get(url, headers=self._auth_header())
        if request.status_code != HTTPStatus.OK:
            raise RequestFailed(request.status_code, request.content.decode())
        return Message.from_dict(request.json())

    def retrieve_all_sms(
        self,
        number_to: str,
        number_from: str,
        date_sent: str,
        date_operation: DateOperation,
    ) -> Iterator[Message]:
        """Retrieve all SMS messages matching the given filters.

        Args:
            number_to: Filter by recipient phone number (empty string for no filter).
            number_from: Filter by sender phone number (empty string for no filter).
            date_sent: Date to filter by in the format required by Twilio.
            date_operation: Date operation type (on, before, or after the date).

        Yields:
            Message instances matching the filter criteria.

        Raises:
            RequestFailed: If any API request fails.
        """
        url = "Messages.json"
        if params := self._all_sms_query_params(number_to, number_from, date_sent, date_operation):
            url = f"{url}?{params}"
        yield from self._valid_content_list(url, "messages", Message)

    @classmethod
    def _all_sms_query_params(
        cls,
        number_to: str,
        number_from: str,
        date_sent: str,
        date_operation: DateOperation,
    ) -> str:
        """Build URL-encoded query parameters for filtering SMS messages.

        Args:
            number_to: Filter by recipient phone number.
            number_from: Filter by sender phone number.
            date_sent: Date to filter by.
            date_operation: Date operation type (on, before, or after).

        Returns:
            URL-encoded query string with non-empty parameters.
        """
        date_field = {
            DateOperation.ON_EXACTLY: "DateSent",
            DateOperation.ON_AND_AFTER: "DateSentAfter",
            DateOperation.ON_AND_BEFORE: "DateSentBefore",
        }[date_operation]

        return urlencode(
            {
                k: v
                for k, v in [
                    (date_field, date_sent),
                    ("To", number_to),
                    ("From", number_from),
                ]
                if v
            }
        )

    def retrieve_media_list(self, message_id: str) -> Iterator[Media]:
        """Retrieve all media items attached to a message.

        Args:
            message_id: The Twilio message SID.

        Yields:
            Media instances for each media item attached to the message.

        Raises:
            RequestFailed: If the API request fails.
        """
        url = f"Messages/{message_id}/Media.json"
        yield from self._valid_content_list(url, "media_list", Media)

    def retrieve_raw_media(self, message_id: str, media_sid: str) -> bytes:
        """Retrieve the raw binary content of a media item.

        Args:
            message_id: The Twilio message SID.
            media_sid: The Twilio media SID.

        Returns:
            Raw binary content of the media file.

        Raises:
            RequestFailed: If the API request fails.
        """
        url = f"Messages/{message_id}/Media/{media_sid}"
        request = self.http.get(url, headers=self._auth_header())
        if request.status_code != HTTPStatus.OK:
            raise RequestFailed(request.status_code, request.content.decode())
        return request.content

    def delete_sms(self, message_id: str) -> bool:
        """Delete a message.

        Args:
            message_id: The Twilio message SID.

        Returns:
            True if the message was successfully deleted.

        Raises:
            RequestFailed: If the API request fails.
        """
        url = f"Messages/{message_id}.json"
        request = self.http.delete(url, headers=self._auth_header())
        if request.status_code != HTTPStatus.NO_CONTENT:
            raise RequestFailed(request.status_code, request.content.decode())
        return True


__exports__ = ()
