import json
from base64 import b64encode
from collections.abc import Mapping
from http import HTTPStatus
from typing import Any

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects import Effect

JSON = dict[str, "JSON"] | list["JSON"] | int | float | str | bool | None


class Response:
    """SimpleAPI response class."""

    def __init__(
        self,
        content: bytes | None = None,
        status_code: HTTPStatus = HTTPStatus.OK,
        headers: Mapping[str, Any] | None = None,
        content_type: str | None = None,
    ) -> None:
        self.content = content
        self.status_code = status_code
        self.headers = {**(headers or {})}

        if content_type:
            self.headers["Content-Type"] = content_type

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
