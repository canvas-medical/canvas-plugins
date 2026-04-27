"""Tests for MCP effect dataclasses."""

import json
from base64 import b64decode

from canvas_generated.messages.effects_pb2 import EffectType
from canvas_sdk.effects.mcp import (
    ImageContent,
    MCPCallToolResponse,
    MCPGetPromptResponse,
    MCPPromptsListResponse,
    MCPReadResourceResponse,
    MCPResourcesListResponse,
    MCPToolsListResponse,
    PromptMessage,
    ResourceContent,
    TextContent,
)


def test_text_content_to_dict() -> None:
    """TextContent serializes to MCP spec shape."""
    assert TextContent(text="hi").to_dict() == {"type": "text", "text": "hi"}


def test_image_content_base64_encodes_data() -> None:
    """ImageContent base64-encodes binary data with mime type."""
    encoded = ImageContent(data=b"\x89PNG", mime_type="image/png").to_dict()
    assert encoded["type"] == "image"
    assert encoded["mimeType"] == "image/png"
    assert b64decode(encoded["data"]) == b"\x89PNG"


def test_resource_content_optional_text_and_blob() -> None:
    """ResourceContent omits absent fields and base64-encodes blobs when present."""
    text_only = ResourceContent(uri="x", mime_type="text/plain", text="hi").to_dict()
    assert text_only == {"uri": "x", "mimeType": "text/plain", "text": "hi"}
    blob = ResourceContent(uri="y", mime_type="image/png", blob=b"\x00\x01").to_dict()
    assert b64decode(blob["blob"]) == b"\x00\x01"
    assert "text" not in blob


def test_prompt_message_nests_content() -> None:
    """PromptMessage wraps the content payload under role+content keys."""
    msg = PromptMessage(role="user", content=TextContent(text="hello")).to_dict()
    assert msg == {"role": "user", "content": {"type": "text", "text": "hello"}}


def test_tools_list_response_apply() -> None:
    """MCPToolsListResponse.apply produces an Effect with the matching type and JSON payload."""
    eff = MCPToolsListResponse(tools=[{"name": "t", "description": "d"}]).apply()
    assert eff.type == EffectType.MCP_TOOLS_LIST_RESPONSE
    assert json.loads(eff.payload) == {"tools": [{"name": "t", "description": "d"}]}


def test_resources_list_response_apply() -> None:
    """MCPResourcesListResponse round-trips through apply."""
    eff = MCPResourcesListResponse(resources=[{"uri": "u"}]).apply()
    assert eff.type == EffectType.MCP_RESOURCES_LIST_RESPONSE
    assert json.loads(eff.payload) == {"resources": [{"uri": "u"}]}


def test_prompts_list_response_apply() -> None:
    """MCPPromptsListResponse round-trips through apply."""
    eff = MCPPromptsListResponse(prompts=[{"name": "p"}]).apply()
    assert eff.type == EffectType.MCP_PROMPTS_LIST_RESPONSE
    assert json.loads(eff.payload) == {"prompts": [{"name": "p"}]}


def test_call_tool_response_success() -> None:
    """A successful tool call serializes content with isError=False and no error key."""
    eff = MCPCallToolResponse(content=[TextContent(text="ok")]).apply()
    payload = json.loads(eff.payload)
    assert eff.type == EffectType.MCP_CALL_TOOL_RESPONSE
    assert payload["isError"] is False
    assert payload["content"][0]["text"] == "ok"
    assert "error" not in payload


def test_call_tool_response_error() -> None:
    """An error tool call carries isError=True and the error dict."""
    eff = MCPCallToolResponse(is_error=True, error={"code": -32001, "message": "denied"}).apply()
    payload = json.loads(eff.payload)
    assert payload["isError"] is True
    assert payload["error"] == {"code": -32001, "message": "denied"}


def test_read_resource_response_carries_error_field() -> None:
    """MCPReadResourceResponse can carry an error payload analogous to call-tool."""
    eff = MCPReadResourceResponse(
        is_error=True, error={"code": -32001, "message": "denied"}
    ).apply()
    payload = json.loads(eff.payload)
    assert eff.type == EffectType.MCP_READ_RESOURCE_RESPONSE
    assert payload["isError"] is True
    assert payload["error"]["code"] == -32001


def test_get_prompt_response_carries_error_field() -> None:
    """MCPGetPromptResponse can carry an error payload analogous to call-tool."""
    eff = MCPGetPromptResponse(is_error=True, error={"code": -32603, "message": "boom"}).apply()
    payload = json.loads(eff.payload)
    assert eff.type == EffectType.MCP_GET_PROMPT_RESPONSE
    assert payload["isError"] is True
    assert payload["error"]["code"] == -32603
