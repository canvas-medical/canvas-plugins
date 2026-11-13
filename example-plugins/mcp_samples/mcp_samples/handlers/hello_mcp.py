from canvas_sdk.effects.mcp import MCPCallToolResponse, TextContent
from canvas_sdk.handlers.mcp import MCP, tool
from canvas_sdk.handlers.mcp.authorize import any_authenticated, has_role


class HelloMCP(MCP):
    """Example MCP handler exposing one open tool and one role-gated tool."""

    @tool(
        name="say_hello",
        description="Greet someone by name.",
        input_schema={
            "type": "object",
            "properties": {"who": {"type": "string"}},
            "required": ["who"],
        },
        authorize=any_authenticated,
    )
    def say_hello(self, arguments: dict) -> MCPCallToolResponse:
        """Greet the named person, defaulting to 'world'."""
        who = arguments.get("who", "world")
        return MCPCallToolResponse(content=[TextContent(text=f"Hello, {who}!")])

    @tool(
        name="post_charge",
        description="Post a billing charge — restricted to billers.",
        input_schema={
            "type": "object",
            "properties": {"amount": {"type": "number"}},
            "required": ["amount"],
        },
        authorize=has_role("biller"),
    )
    def post_charge(self, arguments: dict) -> MCPCallToolResponse:
        """Post a billing charge for the given amount."""
        amount = arguments.get("amount", 0)
        return MCPCallToolResponse(content=[TextContent(text=f"Posted charge of ${amount:.2f}")])
