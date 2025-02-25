from base64 import b64decode
from typing import TYPE_CHECKING

from .exceptions import (
    AuthenticationSchemeError,
    InvalidCredentialsFormatError,
    NoAuthorizationHeaderError,
)

if TYPE_CHECKING:
    from .api import Request


class Credentials:
    """
    Credentials base class.

    Performs no parsing of the request Authorization header. This class can be used as a base class
    for defining custom credentials classes, or can be specified by a developer as the credentials
    class if they wish to just access the request directly in their authentication method.
    """

    def __init__(self, request: "Request") -> None:
        pass


class BasicCredentials(Credentials):
    """
    Basic authentication credentials class.

    Parses and decodes the username and password from the request Authorization header and saves
    them as attributes.
    """

    def __init__(self, request: "Request") -> None:
        super().__init__(request)

        self.username = None
        self.password = None

        authorization = request.headers.get("Authorization")
        if not authorization:
            raise NoAuthorizationHeaderError

        scheme, delimiter, value = authorization.partition(" ")
        if delimiter != " ":
            raise AuthenticationSchemeError
        if scheme.lower() != "basic":
            raise AuthenticationSchemeError

        try:
            value = b64decode(value.encode()).decode()
        except Exception as exception:
            raise InvalidCredentialsFormatError from exception

        username, delimiter, password = value.partition(":")
        if delimiter != ":":
            raise InvalidCredentialsFormatError
        if not username or not password:
            raise InvalidCredentialsFormatError

        self.username = username
        self.password = password


class BearerCredentials(Credentials):
    """
    Bearer authentication credentials class.

    Parses the token from the request Authorization header and saves it as an attribute.
    """

    def __init__(self, request: "Request") -> None:
        super().__init__(request)

        self.token = None

        authorization = request.headers.get("Authorization")
        if not authorization:
            raise NoAuthorizationHeaderError

        scheme, delimiter, token = authorization.partition(" ")
        if delimiter != " ":
            raise AuthenticationSchemeError
        if scheme.lower() != "bearer":
            raise AuthenticationSchemeError
        if not token:
            raise InvalidCredentialsFormatError

        self.token = token


class APIKeyCredentials(Credentials):
    """
    API Key credentials class.

    Obtains the API key from the request Authorization header and saves it as an attribute.

    The default header name is "Authorization", but can be changed by overriding the HEADER_NAME
    class variable in subclasses.
    """

    HEADER_NAME = "Authorization"

    def __init__(self, request: "Request") -> None:
        super().__init__(request)

        if self.HEADER_NAME not in request.headers:
            raise NoAuthorizationHeaderError

        self.key = request.headers.get(self.HEADER_NAME)
        if not self.key:
            raise InvalidCredentialsFormatError
