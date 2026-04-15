from typing import Annotated, Any

from pydantic import Field

from canvas_generated.messages.effects_pb2 import Effect
from canvas_sdk.effects.base import EffectType, _BaseEffect


class HttpRequest(_BaseEffect):
    """Make an HTTP request from a plugin with optional inline effect chaining.

    The platform will execute the HTTP request and, based on the response status,
    run the corresponding on_success (2xx) or on_failure (non-2xx/error) effects.

    The URL must be included in the plugin's url_permissions.

    Example usage::

        http_effect = HttpRequest(
            url="https://api.example.com/submit",
            method="POST",
            headers={"Authorization": "Bearer token"},
            body=json.dumps({"key": "value"}),
            on_success=[
                MoveClaimToQueue(claim_id=claim_id, queue="Filed").apply(),
            ],
            on_failure=[
                AddClaimComment(claim_id=claim_id, comment="Failed").apply(),
            ],
            delay_seconds=60,
        )
        return [http_effect.apply()]
    """

    class Meta:
        effect_type = EffectType.HTTP_REQUEST

    url: str
    method: Annotated[str, Field(pattern="^(GET|POST|PUT|PATCH|DELETE)$")] = "GET"
    headers: dict[str, str] | None = None
    body: str | None = None
    on_success: list[Effect] | None = None
    on_failure: list[Effect] | None = None

    class Config:
        arbitrary_types_allowed = True

    @property
    def values(self) -> dict[str, Any]:
        """Serialize the HTTP request details and chained effects into the payload."""
        v: dict[str, Any] = {
            "url": self.url,
            "method": self.method,
            "headers": self.headers or {},
            "body": self.body or "",
        }
        if self.on_success:
            v["on_success"] = [{"type": e.type, "payload": e.payload} for e in self.on_success]
        if self.on_failure:
            v["on_failure"] = [{"type": e.type, "payload": e.payload} for e in self.on_failure]
        return v


__exports__ = ("HttpRequest",)
