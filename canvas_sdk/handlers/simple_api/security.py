from __future__ import annotations

from base64 import b64decode
from collections.abc import Mapping
from enum import StrEnum
from secrets import compare_digest
from typing import TYPE_CHECKING, Any, Protocol, TypeAlias

from logger import log
from plugin_runner.exceptions import PluginError

from .exceptions import (
    AuthenticationSchemeError,
    InvalidCredentialsError,
    InvalidCredentialsFormatError,
    NoAuthorizationHeaderError,
)

if TYPE_CHECKING:
    from .api import Request
    from .tools import CaseInsensitiveMultiDict


class Credentials:
    """
    Credentials base class.

    Performs no parsing of the request Authorization header. This class can be used as a base class
    for defining custom credentials classes, or can be specified by a developer as the credentials
    class if they wish to just access the request directly in their authentication method.
    """

    def __init__(self, request: Request) -> None:
        pass


class BasicCredentials(Credentials):
    """
    Basic authentication credentials class.

    Parses and decodes the username and password from the request Authorization header and saves
    them as attributes.
    """

    def __init__(self, request: Request) -> None:
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

    def __init__(self, request: Request) -> None:
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

    def __init__(self, request: Request) -> None:
        super().__init__(request)

        if self.HEADER_NAME not in request.headers:
            raise NoAuthorizationHeaderError

        key = request.headers.get(self.HEADER_NAME)
        if not key:
            raise InvalidCredentialsFormatError

        self.key = key


class PortalAccessLevel(StrEnum):
    """
    How much a login may do in one area of the patient's chart.

    Levels compare by how much they allow, NONE < VIEW < ACT, and NONE is falsy.
    """

    NONE = "none"
    VIEW = "view"
    ACT = "act"

    def __lt__(self, other: object) -> bool:
        return _rank(self) < _rank(other)

    def __le__(self, other: object) -> bool:
        return _rank(self) <= _rank(other)

    def __gt__(self, other: object) -> bool:
        return _rank(self) > _rank(other)

    def __ge__(self, other: object) -> bool:
        return _rank(self) >= _rank(other)

    def __bool__(self) -> bool:
        return _rank(self) > 0


_PORTAL_ACCESS_RANKS = {
    PortalAccessLevel.NONE: 0,
    PortalAccessLevel.VIEW: 1,
    PortalAccessLevel.ACT: 2,
}

_PORTAL_AREAS = ("appointments", "messaging", "clinical", "billing")

# The least level, by area, that a login acting on a patient's chart needs there.
PortalAccessRequirement: TypeAlias = Mapping[str, PortalAccessLevel | str]


def _rank(level: object) -> int:
    if not isinstance(level, str):
        raise TypeError(f"Cannot compare a portal access level with {type(level).__name__}")
    return _PORTAL_ACCESS_RANKS[PortalAccessLevel(level)]


class PortalAccess:
    """
    What a login may do on the patient's chart, from the headers Canvas sets.

    When another login, such as a parent's, acts on a patient's chart, acting_user_id names it and
    each area is limited to the access it was given; an area Canvas didn't name, or a level it
    doesn't recognize, counts as none. A patient on their own chart may do everything, and a
    request without a patient session may do nothing.
    """

    AREAS = _PORTAL_AREAS

    def __init__(self, headers: CaseInsensitiveMultiDict) -> None:
        patient_session = headers.get("canvas-logged-in-user-type") == "Patient" and bool(
            headers.get("canvas-logged-in-user-id")
        )

        # The CanvasUser dbid of the login acting on the patient's chart, when it isn't theirs.
        self.acting_user_id: str | None = (
            (headers.get("canvas-logged-in-acting-user-id") or None) if patient_session else None
        )

        self._levels: dict[str, PortalAccessLevel] = {}
        for area in _PORTAL_AREAS:
            if not patient_session:
                level = PortalAccessLevel.NONE
            elif not self.acting_user_id:
                level = PortalAccessLevel.ACT
            else:
                try:
                    level = PortalAccessLevel(headers.get(f"canvas-logged-in-access-{area}"))
                except ValueError:
                    level = PortalAccessLevel.NONE
            self._levels[area] = level

    def level(self, area: str) -> PortalAccessLevel:
        """How much the login may do in one area of the chart."""
        if area not in self._levels:
            raise ValueError(f"Unknown portal area: {area}")
        return self._levels[area]

    def allows(self, area: str, level: PortalAccessLevel | str) -> bool:
        """Whether the login may do at least `level` in one area of the chart."""
        return self.level(area) >= PortalAccessLevel(level)


def validate_portal_access(
    portal_access: PortalAccessRequirement | None, owner: str
) -> dict[str, PortalAccessLevel] | None:
    """Check a declared portal access requirement, raising PluginError if it can't be met."""
    if portal_access is None:
        return None

    if not isinstance(portal_access, Mapping):
        raise PluginError(f"The portal access for {owner} must be a mapping of area to level")

    validated = {}
    for area, level in portal_access.items():
        if area not in _PORTAL_AREAS:
            expected = ", ".join(_PORTAL_AREAS)
            raise PluginError(
                f"Unknown portal area {area!r} for {owner}; expected one of {expected}"
            )
        try:
            validated[area] = PortalAccessLevel(level)
        except ValueError as error:
            raise PluginError(
                f"Unknown portal access level {level!r} for {owner}; expected none, view or act"
            ) from error

    return validated


def admits_portal_access(
    portal_access: PortalAccess, required: Mapping[str, PortalAccessLevel] | None
) -> bool:
    """
    Whether a handler that requires `required` admits the login.

    A login acting on someone else's chart is refused unless the handler declared the access it
    requires, even an empty one. Anyone else is left to the handler's authenticate method.
    """
    if not portal_access.acting_user_id:
        return True

    if required is None:
        return False

    return all(portal_access.allows(area, level) for area, level in required.items())


class SessionCredentials(Credentials):
    """
    Session credentials class.

    Looks for headers set by Canvas with information about the logged in user based on browser
    cookies and session information in the Canvas database. These headers are removed if received by
    the client and intentionally set by Canvas only if there is a valid session from an active user.

    One must look at the type of user in order to understand what the id refers to – a patient or a
    staff member. For a patient, the id is the patient whose chart the request acts on. When another
    login, such as a parent's, acts on a patient's chart, the id is that patient's, not the parent's:
    portal_access.acting_user_id names the login that is acting, and portal_access says how much it
    may do there. Credit what the request does to acting_user_id when it is set.

    If a SimpleAPI handler is protected by SessionCredentials, the non-presence of these headers
    results in an unauthorized response. Users of SessionCredentials will likely wish to further
    restrict access based on the type of user (patient or staff) and perhaps based on the roles
    associated with the user. This logic is the concern of the implementer of the handler's
    authenticate method.
    """

    def __init__(self, request: Request) -> None:
        super().__init__(request)

        if (
            "canvas-logged-in-user-type" not in request.headers
            or "canvas-logged-in-user-id" not in request.headers
        ):
            raise InvalidCredentialsError

        self.logged_in_user = {
            "id": request.headers.get("canvas-logged-in-user-id"),
            "type": request.headers.get("canvas-logged-in-user-type"),
        }
        self.portal_access = request.portal_access


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


class StaffSessionAuthMixin(AuthSchemeMixin):
    """
    Staff Session authentication scheme mixin.

    Provides an implementation of the authenticate method that ensures only logged in staff members
    can access the urls provided by this handler. It only cares that they are a staff, with no
    regard to roles or any other permissioning schemes.
    """

    def authenticate(self, credentials: SessionCredentials) -> bool:  # type: ignore[override]
        """Authenticate the request."""
        if credentials.logged_in_user["type"] != "Staff":
            raise InvalidCredentialsError
        return True


class PatientSessionAuthMixin(AuthSchemeMixin):
    """
    Patient Session authentication scheme mixin.

    Provides an implementation of the authenticate method that ensures only logged in patients can
    access the urls provided by this handler. It only cares that they are a patient, with no regard
    any other information. Another login acting on a patient's chart, such as a parent's, is refused
    unless the handler or route declares the portal access it requires; see SimpleAPI.PORTAL_ACCESS.
    """

    def authenticate(self, credentials: SessionCredentials) -> bool:  # type: ignore[override]
        """Authenticate the request."""
        if credentials.logged_in_user["type"] != "Patient":
            raise InvalidCredentialsError
        return True


__exports__ = (
    "Credentials",
    "BasicCredentials",
    "BearerCredentials",
    "APIKeyCredentials",
    "AuthSchemeMixin",
    "BasicAuthMixin",
    "APIKeyAuthMixin",
    "SessionCredentials",
    "StaffSessionAuthMixin",
    "PatientSessionAuthMixin",
    "PortalAccess",
    "PortalAccessLevel",
)
