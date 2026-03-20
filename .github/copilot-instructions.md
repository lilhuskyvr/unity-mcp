# MCP for Unity — Copilot Instructions

## Project Overview

MCP for Unity bridges AI assistants (Claude, Cursor, VS Code Copilot, Windsurf) with the Unity Editor via the Model Context Protocol. Two codebases, one system:

- `Server/` — Python MCP server built on [FastMCP](https://gofastmcp.com)
- `MCPForUnity/` — Unity C# Editor package

## Architecture

```
AI Assistant → MCP Protocol (stdio/HTTP) → Python Server → WebSocket + HTTP → Unity Editor Plugin → Unity Editor API
```

### Three Layers (Python Side)

| Layer | Location | Framework | Purpose |
|-------|----------|-----------|---------|
| MCP Tools | `Server/src/services/tools/` | FastMCP (`@mcp_for_unity_tool`) | Exposed to AI assistants |
| CLI Commands | `Server/src/cli/commands/` | Click (`@click.command`) | Terminal interface |
| Resources | `Server/src/services/resources/` | FastMCP (`@mcp_for_unity_resource`) | Read-only state |

These layers are NOT auto-generated from each other. MCP tools call Unity via WebSocket (`send_with_unity_instance`). CLI commands call Unity via HTTP (`run_command`). Both route to the same C# `HandleCommand` methods.

### Transport Modes

- **Stdio**: Single-agent, separate Python process per client, legacy TCP bridge.
- **HTTP**: Multi-agent, single shared server, WebSocket hub at `/hub/plugin`, session isolation via `client_id`.

## Code Philosophy

1. **Domain Symmetry** — Python MCP tools mirror C# Editor tools (`manage_material.py` ↔ `ManageMaterial.cs`).
2. **Minimal Abstraction** — No premature helpers. Three similar lines beat a helper used once. Abstract only at 3+ use cases.
3. **Delete Rather Than Deprecate** — Remove dead code completely. No `_unused` renames or backwards-compat shims.
4. **Test Coverage Required** — Every new feature needs tests.
5. **Keep Tools Focused** — One tool does one thing well. Resist bloating APIs.
6. **Resources for Reading** — Resources should be quick, focused, and LLM-friendly.

## Adding a New Tool (Checklist)

1. Python MCP tool: `Server/src/services/tools/manage_<domain>.py` using `@mcp_for_unity_tool`
2. Python CLI commands: `Server/src/cli/commands/<domain>.py` using Click
3. C# implementation: `MCPForUnity/Editor/Tools/Manage<Domain>.cs` with `[McpForUnityTool]`
4. Python tests: `Server/tests/test_manage_<domain>.py`
5. Unity tests: `TestProjects/UnityMCPTests/Assets/Tests/`
6. Manifest entry: Add tool name and description to `manifest.json` `tools` array

## Commands

```bash
# Python tests
cd Server && uv run pytest tests/ -v
cd Server && uv run pytest tests/test_manage_material.py -v
cd Server && uv run pytest tests/ -k "test_create_material" -v
```

## What NOT To Do

- Don't add features without tests
- Don't create helper functions for one-time operations
- Don't add error handling for impossible scenarios
- Don't add docstrings/comments to code you didn't change
- Don't commit to `main` directly — branch off `beta` for PRs
