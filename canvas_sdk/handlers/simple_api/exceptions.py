class SimpleAPIException(Exception):
    """Base class for all SimpleAPI exceptions."""

    def __init__(self, message: str) -> None:
        super().__init__(message)


class AuthenticationError(SimpleAPIException):
    """Base class for all authentication exceptions."""

    pass


class NoAuthorizationHeaderError(AuthenticationError):
    """Exception class for requests without an Authorization header."""

    def __init__(self) -> None:
        super().__init__("Request has no Authorization header")


class AuthenticationSchemeError(AuthenticationError):
    """Exception class for requests that do not have a valid authentication scheme."""

    def __init__(self) -> None:
        super().__init__("Authorization header has no recognized authentication scheme")


class InvalidCredentialsFormatError(AuthenticationError):
    """Exception class for requests that have incorrectly-formatted credentials."""

    def __init__(self) -> None:
        super().__init__("Provided credentials are incorrectly formatted")


class InvalidCredentialsError(AuthenticationError):
    """Exception class for requests that have invalid credentials."""

    def __init__(self) -> None:
        super().__init__("Provided credentials are invalid")


__exports__ = (
    "SimpleAPIException",
    "AuthenticationError",
    "NoAuthorizationHeaderError",
    "AuthenticationSchemeError",
    "InvalidCredentialsFormatError",
    "InvalidCredentialsError",
)
