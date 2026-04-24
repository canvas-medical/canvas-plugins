from enum import StrEnum
from typing import Annotated, Any

from pydantic import Field

from canvas_sdk.effects.base import EffectType, _BaseEffect


class HttpMethod(StrEnum):
    """HTTP method for an HttpRequestEffect."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


class HttpRequestEffect(_BaseEffect):
    """Make an HTTP request from a plugin.

    The platform will execute the HTTP request on behalf of the plugin.
    The URL must be included in the plugin's url_permissions.

    Header values are transmitted as-is — store credentials in the plugin's
    ``secrets`` and reference them here rather than hard-coding them.

    Example usage::

        http_effect = HttpRequestEffect(
            url="https://api.example.com/submit",
            method=HttpMethod.POST,
            headers={"Authorization": "Bearer token"},
            body=json.dumps({"key": "value"}),
            retry_on_status_codes=[500, 502]
        )
        return [http_effect.apply().set_async(delay_seconds=0)]
    """

    class Meta:
        effect_type = EffectType.HTTP_REQUEST

    url: Annotated[str, Field(min_length=1)]
    method: HttpMethod = Field(default=HttpMethod.GET, strict=False)
    headers: dict[str, str] | None = None
    body: str | None = None
    retry_on_status_codes: list[Annotated[int, Field(ge=100, le=599)]] | None = None

    @property
    def values(self) -> dict[str, Any]:
        """Serialize the HTTP request details into the payload."""
        return {
            "url": self.url,
            "method": self.method,
            "headers": self.headers or {},
            "body": self.body or "",
            "retry_on_status_codes": self.retry_on_status_codes or [],
        }

    @property
    def effect_payload(self) -> dict[str, Any]:
        """The payload to be sent for the Effect."""
        return {
            "data": self.values,
            "async_props": {"retry_on_status_codes": self.retry_on_status_codes},
        }


__exports__ = ("HttpMethod", "HttpRequestEffect")
