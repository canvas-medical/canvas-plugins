import json
import re
from base64 import b64encode
from collections.abc import Mapping, Sequence
from http import HTTPStatus
from typing import Any

from pydantic_core import InitErrorDetails

from canvas_sdk.effects import Effect, EffectType, _BaseEffect

JSON = Mapping[str, "JSON"] | Sequence["JSON"] | int | float | str | bool | None


class Response(_BaseEffect):
    """SimpleAPI response class."""

    content: bytes | None
    status_code: int
    headers: dict[str, Any] | None

    def __init__(
        self,
        content: bytes | None = None,
        status_code: HTTPStatus = HTTPStatus.OK,
        headers: Mapping[str, Any] | None = None,
        content_type: str | None = None,
    ) -> None:
        headers = {**(headers or {})}
        if content_type:
            headers["Content-Type"] = content_type

        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,  # type: ignore[call-arg]
        )

    def apply(self) -> Effect:
        """Convert the response into an effect."""
        payload = {
            "headers": self.headers or {},
            "body": b64encode(self.content or b"").decode(),
            "status_code": self.status_code,
        }

        return Effect(type=EffectType.SIMPLE_API_RESPONSE, payload=json.dumps(payload))


class JSONResponse(Response):
    """SimpleAPI JSON response class."""

    def __init__(
        self,
        content: JSON,
        status_code: HTTPStatus = HTTPStatus.OK,
        headers: Mapping[str, Any] | None = None,
    ):
        super().__init__(
            json.dumps(content).encode(), status_code, headers, content_type="application/json"
        )


class PlainTextResponse(Response):
    """SimpleAPI plain text response class."""

    def __init__(
        self,
        content: str,
        status_code: HTTPStatus = HTTPStatus.OK,
        headers: Mapping[str, Any] | None = None,
    ):
        super().__init__(content.encode(), status_code, headers, content_type="text/plain")


class HTMLResponse(Response):
    """SimpleAPI HTML response class."""

    def __init__(
        self,
        content: str,
        status_code: HTTPStatus = HTTPStatus.OK,
        headers: Mapping[str, Any] | None = None,
    ):
        super().__init__(content.encode(), status_code, headers, content_type="text/html")


class AcceptConnection(_BaseEffect):
    """AcceptConnection effect."""

    class Meta:
        effect_type = EffectType.SIMPLE_API_WEBSOCKET_ACCEPT


class DenyConnection(_BaseEffect):
    """DenyConnection effect."""

    message: str | None = None

    class Meta:
        effect_type = EffectType.SIMPLE_API_WEBSOCKET_DENY

    @property
    def values(self) -> dict[str, Any]:
        """Make the payload."""
        return {"message": self.message} if self.message else {}


class Broadcast(_BaseEffect):
    """Broadcast effect."""

    class Meta:
        effect_type = EffectType.SIMPLE_API_WEBSOCKET_BROADCAST

    channel: str
    message: dict[str, Any]

    @property
    def values(self) -> dict[str, Any]:
        """Make the payload."""
        return {"channel": self.channel, "message": self.message}

    def is_valid_channel_name(self) -> bool:
        """Check if the channel name is valid."""
        return re.fullmatch(r"\w+", self.channel) is not None

    def _get_error_details(self, method: Any) -> list[InitErrorDetails]:
        errors = super()._get_error_details(method)

        if not self.is_valid_channel_name():
            errors.append(
                self._create_error_detail(
                    "value",
                    "Invalid channel name. Channel name must be alphanumeric and can contain underscores.",
                    self.channel,
                )
            )

        return errors


__exports__ = (
    "JSON",
    "Response",
    "JSONResponse",
    "PlainTextResponse",
    "HTMLResponse",
    "AcceptConnection",
    "DenyConnection",
    "Broadcast",
)
