class RequestFailed(RuntimeError):
    """Exception raised when a SendGrid API request fails."""

    def __init__(self, status_code: int, message: str):
        """Initialize RequestFailed exception with status code and message."""
        super().__init__(message)
        self.status_code = status_code
        self.message = message


__exports__ = ()
