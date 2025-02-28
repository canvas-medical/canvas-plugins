from base64 import b64decode
from secrets import compare_digest
from typing import TYPE_CHECKING, Any, Protocol

from logger import log

from .exceptions import (
    AuthenticationSchemeError,
    InvalidCredentialsError,
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

        key = request.headers.get(self.HEADER_NAME)
        if not key:
            raise InvalidCredentialsFormatError

        self.key = key


class AuthSchemeMixin(Protocol):
    """Protocol for authentication scheme mixins."""

    secrets: dict[str, str]

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

    def authenticate(self, credentials: Credentials) -> bool:
        """Authenticate the request."""
        ...


class BasicAuthMixin(AuthSchemeMixin):
    """
    Basic authentication scheme mixin.

    Provides an implementation of the authenticate method for Basic authentication.
    """

    USERNAME_SECRET_NAME = "simpleapi-basic-username"
    PASSWORD_SECRET_NAME = "simpleapi-basic-password"

    def authenticate(self, credentials: BasicCredentials) -> bool:  # type: ignore[override]
        """Authenticate the request."""
        try:
            username = self.secrets[self.USERNAME_SECRET_NAME]
            password = self.secrets[self.PASSWORD_SECRET_NAME]
        except KeyError as error:
            log.error(
                "SimpleAPI secrets for Basic authentication are not set; please set values for "
                f"{self.USERNAME_SECRET_NAME} and {self.PASSWORD_SECRET_NAME}"
            )
            raise InvalidCredentialsError from error

        if not (
            compare_digest(credentials.username.encode(), username.encode())
            and compare_digest(credentials.password.encode(), password.encode())
        ):
            raise InvalidCredentialsError

        return True


class APIKeyAuthMixin(AuthSchemeMixin):
    """
    API Key authentication scheme mixin.

    Provides an implementation of the authenticate method for API Key authentication.
    """

    API_KEY_SECRET_NAME = "simpleapi-api-key"

    def authenticate(self, credentials: APIKeyCredentials) -> bool:  # type: ignore[override]
        """Authenticate the request."""
        try:
            api_key = self.secrets[self.API_KEY_SECRET_NAME]
        except KeyError as error:
            log.error(
                f"SimpleAPI secret for API Key authentication is not set; please set a value for "
                f"{self.API_KEY_SECRET_NAME}"
            )
            raise InvalidCredentialsError from error

        if not compare_digest(credentials.key.encode(), api_key.encode()):
            raise InvalidCredentialsError

        return True
