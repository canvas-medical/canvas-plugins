from base64 import b64decode
from typing import TYPE_CHECKING

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
            return

        scheme, delimiter, value = authorization.partition(" ")
        if delimiter != " ":
            return
        if scheme.lower() != "basic":
            return

        try:
            value = b64decode(value.encode()).decode()
        except Exception:
            return

        username, delimiter, password = value.partition(":")
        if delimiter != ":":
            return
        if not username or not password:
            return

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
            return

        scheme, delimiter, token = authorization.partition(" ")
        if delimiter != " ":
            return
        if scheme.lower() != "bearer":
            return
        if not token:
            return

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

        self.key = request.headers.get(self.HEADER_NAME) or None
