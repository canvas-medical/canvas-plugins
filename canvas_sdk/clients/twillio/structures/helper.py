from datetime import datetime
from urllib.parse import parse_qs

from canvas_sdk.clients.twillio.constants.constants import Constants


class Helper:
    """Utility class."""

    @classmethod
    def from_datetime_or_none(cls, value: datetime | None, date_format: str) -> str | None:
        """Convert a datetime to a formatted string, or return None if the value is None.

        Args:
            value: The datetime to convert or None.
            date_format: The format string to use for conversion.

        Returns:
            Formatted date string or None.
        """
        if isinstance(value, datetime):
            return value.strftime(date_format)
        return None

    @classmethod
    def from_datetime(cls, value: datetime, date_format: str) -> str:
        """Convert a datetime to a formatted string.

        Args:
            value: The datetime to convert.
            date_format: The format string to use for conversion.

        Returns:
            Formatted date string.
        """
        return value.strftime(date_format)

    @classmethod
    def to_datetime_or_none(cls, data: dict, key: str) -> datetime | None:
        """Parse a datetime from a dictionary key, or return None if the key is missing.

        Args:
            data: Dictionary containing the date string.
            key: The key to look up in the dictionary.

        Returns:
            Parsed datetime or None.
        """
        if data.get(key):
            return datetime.strptime(data[key], Constants.twilio_date)
        return None

    @classmethod
    def to_datetime(cls, data: dict, key: str) -> datetime:
        """Parse a datetime from a dictionary key.

        Args:
            data: Dictionary containing the date string.
            key: The key to look up in the dictionary.

        Returns:
            Parsed datetime object.
        """
        return datetime.strptime(data[key], Constants.twilio_date)

    @classmethod
    def parse_body(cls, raw_body: str) -> dict:
        """Parse URL-encoded body into a dictionary.

        Args:
            raw_body: URL-encoded string from Twilio callback.

        Returns:
            Dictionary with parsed key-value pairs.
        """
        return {
            key: values[0] if len(values) == 1 else values
            for key, values in parse_qs(raw_body, keep_blank_values=True).items()
        }


__exports__ = ()
