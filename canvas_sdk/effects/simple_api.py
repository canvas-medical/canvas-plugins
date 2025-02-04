import json
from collections.abc import Mapping
from typing import Any

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects import Effect


class SimpleAPIResponse:
    """SimpleAPI response class."""

    def __init__(
        self, content: Mapping[str, Any], status_code: int, headers: Mapping[str, Any] | None = None
    ) -> None:
        self._content = content
        self._status_code = status_code
        self._headers = {**(headers or {}), "Content-Type": "application/json"}

    def apply(self) -> Effect:
        """Convert the response into an effect."""
        payload = {
            "body": self._content,
            "status_code": self._status_code,
            "headers": self._headers or {},
        }

        return Effect(type=EffectType.SIMPLE_API_RESPONSE, payload=json.dumps(payload))
