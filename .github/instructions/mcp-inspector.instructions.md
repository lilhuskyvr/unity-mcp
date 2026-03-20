---
name: 'MCP Inspector Testing'
description: 'How to use npx @modelcontextprotocol/inspector to test the MCP server'
applyTo: 'Server/**'
---
# Testing the MCP Server with MCP Inspector

Use [MCP Inspector](https://github.com/modelcontextprotocol/inspector) to interactively explore and test MCP tools and resources exposed by the server.

## Prerequisites

- Node.js installed (for `npx`)
- The MCP server running in HTTP mode (see below)
- Unity Editor open with the MCP for Unity plugin active (for live tool calls)

## Start the HTTP Server

The inspector connects over HTTP/SSE, so start the server in HTTP transport mode:

```bash
cd Server
uv run --directory C:\path\to\unity-mcp\Server C:\path\to\unity-mcp\Server\src\main.py --transport http --http-url http://localhost:8080
```

Or if the server is already running (e.g. started by Unity), skip this step.

## Launch the Inspector

```bash
npx @modelcontextprotocol/inspector http://localhost:8080/mcp
```

This opens the inspector UI in your browser. From there you can:

- **List tools** — browse all registered MCP tools and their input schemas
- **Call tools** — invoke a tool with custom JSON parameters and inspect the response
- **List resources** — browse all registered resources
- **Read resources** — fetch a resource and inspect its content

## Common Options

```bash
# Use a custom proxy port (default is 6277)
npx @modelcontextprotocol/inspector --proxy-port 6300 http://localhost:8080/mcp

# Point to a different server URL
npx @modelcontextprotocol/inspector http://localhost:9000/mcp
```

## Workflow for Testing a New Tool

1. Start the HTTP server (see above).
2. Run the inspector pointing at `http://localhost:8080/mcp`.
3. In the **Tools** tab, find your tool by name.
4. Fill in the required parameters and click **Run Tool**.
5. Verify the response matches the expected shape.
6. Check the Unity console for any errors triggered by the tool call.

## Checking If the Server Is Running

```powershell
# Check if port 8080 is listening
netstat -ano | Select-String "127.0.0.1:8080\s.*LISTENING"
```

## Killing a Stuck Server Process

```powershell
$p = (netstat -ano | Select-String "127.0.0.1:8080\s.*LISTENING" | ForEach-Object { ($_ -split '\s+')[-1] } | Select-Object -First 1)
if ($p) { Stop-Process -Id $p -Force; Write-Host "Killed $p" } else { Write-Host "Not found" }
```

## Notes

- The inspector only works with HTTP transport (`--transport http`), not stdio.
- The server endpoint is `/mcp` (e.g. `http://localhost:8080/mcp`).
- If tools are missing, check that the relevant tool group is enabled via `manage_tools`.
- The inspector does **not** replace `pytest` — always run `uv run pytest tests/ -v` before PRs.
