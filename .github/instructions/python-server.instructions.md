---
name: 'Python MCP Server'
description: 'Conventions for the Python MCP server codebase (FastMCP, transport, services)'
applyTo: 'Server/**/*.py'
---
# Python Server Conventions

## Framework

The server uses [FastMCP](https://gofastmcp.com) (standalone, not the SDK-embedded version). Tools are registered via a custom `@mcp_for_unity_tool` decorator that wraps `@mcp.tool` with group visibility, telemetry, and logging.

## Tool Registration

Tools live in `Server/src/services/tools/` and are **auto-discovered** at startup via `pkgutil.iter_modules`. The decorator `@mcp_for_unity_tool` registers them in a global `_tool_registry`. Then `register_all_tools()` in `Server/src/services/tools/__init__.py` iterates the registry and calls `mcp.tool()` for each.

### Standard tool pattern:
```python
from typing import Annotated, Literal, Any
from fastmcp import Context
from mcp.types import ToolAnnotations
from services.registry import mcp_for_unity_tool
from services.tools import get_unity_instance_from_context
from transport.unity_transport import send_with_unity_instance
from transport.legacy.unity_connection import async_send_command_with_retry

@mcp_for_unity_tool(
    description="Does something in Unity.",
    group="core",  # core (default), vfx, animation, ui, scripting_ext, testing, probuilder, docs
    annotations=ToolAnnotations(title="My Tool", readOnlyHint=True),
)
async def my_tool(
    ctx: Context,
    action: Annotated[Literal["create", "delete"], "Action to perform"],
) -> dict[str, Any]:
    unity_instance = await get_unity_instance_from_context(ctx)
    params = {"action": action}
    response = await send_with_unity_instance(
        async_send_command_with_retry, unity_instance, "my_tool", params
    )
    return response
```

### Key decorator parameters:
- `group="core"` — Tool group for visibility. Only `"core"` is enabled by default. Use `None` for always-visible meta-tools.
- `unity_target="self"` (default) — Tool follows its own enabled state. `None` = server-only, always visible.
- `name` — Defaults to function name if omitted.
- `annotations` — `ToolAnnotations` for MCP client hints (`readOnlyHint`, `destructiveHint`).
- `tags` — Merged with group tag automatically.

## Tool Groups

Valid groups: `core`, `docs`, `vfx`, `animation`, `ui`, `scripting_ext`, `testing`, `probuilder`. `None` = always visible.

## Resources

Resources use `@mcp_for_unity_resource` in `Server/src/services/resources/`. They provide read-only state to AI assistants.

## Return Types

- Tools that communicate with Unity return `dict` (raw Unity response).
- Server-only tools may return `MCPResponse` (Pydantic model with `success`, `message`, `data`).

## Imports

- Prefer `from services.registry import mcp_for_unity_tool` over direct FastMCP imports.
- Use `from transport.unity_transport import send_with_unity_instance` for Unity communication.
- Use `from transport.legacy.unity_connection import async_send_command_with_retry` for the legacy TCP bridge.

## Type Annotations

Use `Annotated` from `typing` with string descriptions for tool parameters. Use `Literal` for action enums.

## Config

`from core.config import config` provides server configuration (transport mode, URLs, etc.).

## Local Development — Running the Server

Always run from the `Server/` directory. If port 8080 is occupied, kill it first:

```bash
kill-port 8080
```

Then start the local dev server:

```bash
cd Server
uv run src/main.py --transport http --http-url http://localhost:8080 --project-scoped-tools
```

- `--project-scoped-tools` enables `execute_custom_tool`, `list_custom_tools`, and the `mcpforunity://custom-tools` resource. Include it whenever working on custom tool features.
- The server binds to `http://localhost:8080`. The MCP endpoint is `http://localhost:8080/mcp`.
- To verify tools with MCP Inspector: `npx @modelcontextprotocol/inspector http://localhost:8080/mcp`
