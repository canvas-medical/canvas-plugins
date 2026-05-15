class RequestFailed(RuntimeError):
    """Exception raised when a Twilio API request fails.

    Attributes:
        status_code: The HTTP status code of the failed request.
        message: The error message describing the failure.
    """

    def __init__(self, status_code: int, message: str):
        """Initialize a RequestFailed exception.

        Args:
            status_code: The HTTP status code of the failed request.
            message: The error message describing the failure.
        """
        super().__init__(message)
        self.status_code = status_code
        self.message = message


__exports__ = ()
