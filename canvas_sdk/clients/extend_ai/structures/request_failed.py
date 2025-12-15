from typing import NamedTuple


class RequestFailed(NamedTuple):
    """Represents a failed API request.

    Attributes:
        status_code: The HTTP status code of the failed request.
        message: The error message describing the failure.
    """

    status_code: int
    message: str

    def to_dict(self) -> dict:
        """Convert this RequestFailed to a dictionary.

        Returns:
            Dictionary representation of the error.
        """
        return {
            "statusCode": self.status_code,
            "message": self.message,
        }


__exports__ = ()
