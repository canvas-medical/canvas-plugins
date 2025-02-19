from abc import ABC, abstractmethod
from base64 import b64decode
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .api import SimpleAPIBase


class AuthenticationScheme(ABC):
    """Abstract base class for authentication schemes."""

    def __init__(self, handler: "SimpleAPIBase", *args: Any, **kwargs: Any) -> None:
        self.handler = handler

    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate the request."""
        raise NotImplementedError


class Basic(AuthenticationScheme, ABC):
    """
    Basic authentication scheme.

    Parses and decodes the username and password from the Authorization header and saves them as
    attributes.
    """

    def __init__(self, handler: "SimpleAPIBase", *args: Any, **kwargs: Any) -> None:
        super().__init__(handler, *args, **kwargs)

        self.username = None
        self.password = None

        authorization = self.handler.request.headers.get("Authorization")
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


class Bearer(AuthenticationScheme, ABC):
    """
    Bearer authentication scheme.

    Parses the token from the Authorization header and saves it as an attribute.
    """

    def __init__(self, handler: "SimpleAPIBase", *args: Any, **kwargs: Any) -> None:
        super().__init__(handler, *args, **kwargs)

        self.token = None

        authorization = self.handler.request.headers.get("Authorization")
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


class APIKey(AuthenticationScheme, ABC):
    """
    API Key authentication scheme.

    Obtains the API key from the Authorization header and saves it as an attribute.

    The default header name is "Authorization", but can be changed by overriding the HEADER_NAME
    class variable in subclasses.
    """

    HEADER_NAME = "Authorization"

    def __init__(self, handler: "SimpleAPIBase", *args: Any, **kwargs: Any) -> None:
        super().__init__(handler, *args, **kwargs)
        self.key = self.handler.request.headers.get(self.HEADER_NAME) or None
