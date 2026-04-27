# mcp_samples

Example MCP handler that exposes two tools to MCP clients via Canvas's `/mcp` endpoint:

- `mcp_samples__say_hello` — open to any authenticated actor.
- `mcp_samples__post_charge` — restricted to actors with the `biller` role.

A non-biller listing tools sees only `say_hello`. Calling `post_charge` directly returns
JSON-RPC `-32001` Unauthorized.

The `mcp_samples__` prefix is applied at the home-app boundary; the plugin code itself only ever
deals with bare names (`say_hello`, `post_charge`).
