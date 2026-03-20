---
name: 'MCP Tool Creation'
description: 'How to create and register new MCP tools (Python side). Covers @mcp_for_unity_tool, manifest.json, and auto-discovery.'
applyTo: 'Server/src/services/tools/**'
---
# Creating MCP Tools

## Auto-Discovery

All `.py` files in `Server/src/services/tools/` (and one level of subdirectories) are auto-imported at startup via `pkgutil.iter_modules`. The `@mcp_for_unity_tool` decorator registers the function into a global registry. Then `register_all_tools()` wraps each with logging, telemetry, and `mcp.tool()`.

**If your module fails to import (e.g. circular import), the tool silently won't register.** Always verify with:
```bash
cd Server && uv run python -c "from services.tools.my_tool import my_tool; print('OK')"
```

## Manifest Registration

Every tool MUST be listed in `manifest.json` under `tools` for VS Code Copilot and MCP Inspector to see it. The manifest is alphabetically ordered. Add your entry:
```json
{
  "name": "my_tool",
  "description": "What the tool does"
}
```

## Tool Template (Unity-connected)

```python
from typing import Annotated, Literal, Any
from fastmcp import Context
from mcp.types import ToolAnnotations
from services.registry import mcp_for_unity_tool
from services.tools import get_unity_instance_from_context
from transport.unity_transport import send_with_unity_instance
from transport.legacy.unity_connection import async_send_command_with_retry

@mcp_for_unity_tool(
    description="Short description of what the tool does.",
    group="core",
    annotations=ToolAnnotations(title="My Tool"),
)
async def my_tool(
    ctx: Context,
    action: Annotated[Literal["create", "read", "update", "delete"], "Action to perform"],
    name: Annotated[str, "Name of the thing"] | None = None,
) -> dict[str, Any]:
    unity_instance = await get_unity_instance_from_context(ctx)
    params = {"action": action}
    if name is not None:
        params["name"] = name
    response = await send_with_unity_instance(
        async_send_command_with_retry, unity_instance, "my_tool", params
    )
    return response
```

## Tool Template (Server-only, no Unity)

For tools that don't communicate with Unity (meta-tools, listing tools):

```python
from fastmcp import Context
from mcp.types import ToolAnnotations
from services.registry import mcp_for_unity_tool

@mcp_for_unity_tool(
    name="my_server_tool",
    description="A server-only tool.",
    unity_target=None,   # Always visible, no Unity filtering
    group=None,          # Always visible, no group toggle
    annotations=ToolAnnotations(title="My Server Tool", readOnlyHint=True),
)
async def my_server_tool(ctx: Context) -> dict:
    return {"success": True, "message": "result"}
```

## Key Rules

- `group=None` + `unity_target=None` = always visible meta-tool (like `set_active_instance`, `manage_tools`).
- `group="core"` = visible by default. Other groups start disabled in HTTP mode.
- Function name = tool name unless `name=` is specified.
- Use `Annotated[type, "description"]` for all parameters — this generates the MCP schema.
- Use `Literal[...]` for action enums so the MCP client knows valid values.
- Return `dict` for Unity responses, or `MCPResponse` for server-only results.
- Always add a corresponding C# handler in `MCPForUnity/Editor/Tools/` if the tool talks to Unity.
