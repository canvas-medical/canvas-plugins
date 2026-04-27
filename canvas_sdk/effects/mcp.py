"""MCP effect dataclasses returned by `MCP` handler methods."""

import json
from base64 import b64encode
from dataclasses import dataclass, field
from typing import Any, Literal

from canvas_sdk.effects import Effect, EffectType


@dataclass
class TextContent:
    """Plain-text content fragment for tool/prompt responses."""

    text: str
    type: Literal["text"] = "text"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to MCP spec wire format."""
        return {"type": self.type, "text": self.text}


@dataclass
class ImageContent:
    """Binary image content fragment with MIME type, base64-encoded on the wire."""

    data: bytes
    mime_type: str
    type: Literal["image"] = "image"

    def to_dict(self) -> dict[str, Any]:
        """Serialize to MCP spec wire format."""
        return {
            "type": self.type,
            "data": b64encode(self.data).decode(),
            "mimeType": self.mime_type,
        }


@dataclass
class ResourceContent:
    """Per-resource payload returned from a `resources/read` call.

    Carries either a `text` body or a `blob` (base64-encoded on the wire) — typically not both.
    """

    uri: str
    mime_type: str
    text: str | None = None
    blob: bytes | None = None

    def to_dict(self) -> dict[str, Any]:
        """Serialize to MCP spec wire format, omitting absent fields."""
        out: dict[str, Any] = {"uri": self.uri, "mimeType": self.mime_type}
        if self.text is not None:
            out["text"] = self.text
        if self.blob is not None:
            out["blob"] = b64encode(self.blob).decode()
        return out


@dataclass
class PromptMessage:
    """A single message returned by a `prompts/get` call."""

    role: Literal["user", "assistant"]
    content: TextContent | ImageContent

    def to_dict(self) -> dict[str, Any]:
        """Serialize to MCP spec wire format."""
        return {"role": self.role, "content": self.content.to_dict()}


def _content_to_dict(item: Any) -> Any:
    return item.to_dict() if hasattr(item, "to_dict") else item


@dataclass
class MCPToolsListResponse:
    """Effect returned by an `MCP` handler in response to `MCP_LIST_TOOLS`."""

    tools: list[dict[str, Any]] = field(default_factory=list)

    def apply(self) -> Effect:
        """Convert this response into a protobuf `Effect`."""
        return Effect(
            type=EffectType.MCP_TOOLS_LIST_RESPONSE,
            payload=json.dumps({"tools": self.tools}),
        )


@dataclass
class MCPResourcesListResponse:
    """Effect returned by an `MCP` handler in response to `MCP_LIST_RESOURCES`."""

    resources: list[dict[str, Any]] = field(default_factory=list)

    def apply(self) -> Effect:
        """Convert this response into a protobuf `Effect`."""
        return Effect(
            type=EffectType.MCP_RESOURCES_LIST_RESPONSE,
            payload=json.dumps({"resources": self.resources}),
        )


@dataclass
class MCPPromptsListResponse:
    """Effect returned by an `MCP` handler in response to `MCP_LIST_PROMPTS`."""

    prompts: list[dict[str, Any]] = field(default_factory=list)

    def apply(self) -> Effect:
        """Convert this response into a protobuf `Effect`."""
        return Effect(
            type=EffectType.MCP_PROMPTS_LIST_RESPONSE,
            payload=json.dumps({"prompts": self.prompts}),
        )


@dataclass
class MCPCallToolResponse:
    """Effect returned by an `MCP` handler in response to `MCP_CALL_TOOL`.

    Successful calls populate `content`; failures set `is_error=True` and `error`.
    """

    content: list[TextContent | ImageContent] = field(default_factory=list)
    is_error: bool = False
    error: dict[str, Any] | None = None

    def apply(self) -> Effect:
        """Convert this response into a protobuf `Effect`."""
        payload: dict[str, Any] = {
            "isError": self.is_error,
            "content": [_content_to_dict(c) for c in self.content],
        }
        if self.error is not None:
            payload["error"] = self.error
        return Effect(
            type=EffectType.MCP_CALL_TOOL_RESPONSE,
            payload=json.dumps(payload),
        )


@dataclass
class MCPReadResourceResponse:
    """Effect returned by an `MCP` handler in response to `MCP_READ_RESOURCE`."""

    contents: list[ResourceContent] = field(default_factory=list)
    is_error: bool = False
    error: dict[str, Any] | None = None

    def apply(self) -> Effect:
        """Convert this response into a protobuf `Effect`."""
        payload: dict[str, Any] = {
            "isError": self.is_error,
            "contents": [c.to_dict() for c in self.contents],
        }
        if self.error is not None:
            payload["error"] = self.error
        return Effect(
            type=EffectType.MCP_READ_RESOURCE_RESPONSE,
            payload=json.dumps(payload),
        )


@dataclass
class MCPGetPromptResponse:
    """Effect returned by an `MCP` handler in response to `MCP_GET_PROMPT`."""

    description: str = ""
    messages: list[PromptMessage] = field(default_factory=list)
    is_error: bool = False
    error: dict[str, Any] | None = None

    def apply(self) -> Effect:
        """Convert this response into a protobuf `Effect`."""
        payload: dict[str, Any] = {
            "isError": self.is_error,
            "description": self.description,
            "messages": [m.to_dict() for m in self.messages],
        }
        if self.error is not None:
            payload["error"] = self.error
        return Effect(
            type=EffectType.MCP_GET_PROMPT_RESPONSE,
            payload=json.dumps(payload),
        )


__exports__ = (
    "TextContent",
    "ImageContent",
    "ResourceContent",
    "PromptMessage",
    "MCPToolsListResponse",
    "MCPResourcesListResponse",
    "MCPPromptsListResponse",
    "MCPCallToolResponse",
    "MCPReadResourceResponse",
    "MCPGetPromptResponse",
)
