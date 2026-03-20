---
name: 'Playwright MCP Testing'
description: 'Always use Playwright MCP to test the MCP server interactively via the browser'
applyTo: 'Server/**'
---
# Testing the MCP Server with Playwright MCP

**You MUST use the Playwright MCP tools (`mcp_playwright_browser_*`) to test the MCP server.** Do not describe steps — actually navigate the browser, interact with the UI, and verify responses.

## Required Workflow

### 1. Ensure the HTTP Server Is Running

The MCP Inspector only works over HTTP. Start the server if it is not already running:

```bash
cd Server
uv run --directory C:\path\to\unity-mcp\Server C:\path\to\unity-mcp\Server\src\main.py --transport http --http-url http://localhost:8080
```

Check the server is up:

```powershell
netstat -ano | Select-String "127.0.0.1:8080\s.*LISTENING"
```

### 2. Start the MCP Inspector and Get the Auth Token

Run the inspector in a terminal and capture its output — the startup logs print a session token and a ready-to-use URL:

```powershell
npx @modelcontextprotocol/inspector http://localhost:8080/mcp *> "$env:TEMP\inspector.log"
```

Then read the token from the log:

```powershell
Get-Content "$env:TEMP\inspector.log"
```

The output looks like:

```
⚙️ Proxy server listening on localhost:6277
🔒 Session token: d74cacafdc92ba85e67e598798667b85b6b16cba903e9db1107bfa63ed25cdb0
🚀 MCP Inspector is up and running at:
   http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=d74cacafdc92ba85e67e598798667b85b6b16cba903e9db1107bfa63ed25cdb0
```

### 3. Navigate to the Inspector with the Auth Token

Use Playwright MCP to open the inspector **with the token in the URL** (avoids the proxy session token prompt):

```
mcp_playwright_browser_navigate → http://localhost:6274/?MCP_PROXY_AUTH_TOKEN=<token>
```

### 4. Configure the Inspector

The correct settings (confirmed working):

| Field | Value |
|---|---|
| Transport Type | **Streamable HTTP** |
| URL | `http://localhost:8080/mcp` |
| Connection Type | **Via Proxy** |

> ⚠️ Do **not** use Connection Type **Direct** — it fails with CORS errors.
> Do **not** use **SSE** transport — the server exposes `/mcp`, not `/sse`.

If the URL field still shows a stale value, use `mcp_playwright_browser_type` to overwrite it (it calls `.fill()` internally).

Click **Connect** and wait for the status to show **Connected**.

### 5. Test a Tool — Step-by-Step

For every tool you want to verify, use this sequence:

1. `mcp_playwright_browser_snapshot` — confirm **Connected** status
2. `mcp_playwright_browser_click` — click the **Tools** tab
3. `mcp_playwright_browser_click` — select the target tool from the list
4. `mcp_playwright_browser_type` — fill in parameter fields
5. `mcp_playwright_browser_click` — click **Run Tool**
6. `mcp_playwright_browser_snapshot` — capture the response panel
7. Assert the response JSON matches the expected shape

### 6. Test a Resource — Step-by-Step

1. `mcp_playwright_browser_click` — click the **Resources** tab
2. `mcp_playwright_browser_click` — select the target resource
3. `mcp_playwright_browser_snapshot` — capture the returned content
4. Assert the content is correct

### 7. Capture Screenshots for Evidence

After every tool/resource call, take a screenshot to document the result:

```
mcp_playwright_browser_take_screenshot
```

### 8. Check Browser Console for Errors

```
mcp_playwright_browser_console_messages
```

Look for any JavaScript errors or failed network requests that indicate a server-side problem.

## Rules

- **Always use Playwright MCP** — never just describe what you would click. Actually do it.
- Always navigate with the full `?MCP_PROXY_AUTH_TOKEN=` URL to skip the auth setup step.
- Use `mcp_playwright_browser_type` (not `mcp_playwright_browser_fill_form`) to set field values — the comboboxes and textboxes in the Inspector UI are not standard `<select>`/`<input>` elements.
- To change the Transport Type or Connection Type, click the combobox first, then click the desired option from the resulting listbox.
- Always take a `mcp_playwright_browser_snapshot` before and after interacting to confirm state changes.
- If the inspector UI is not loading, check the server is running and the proxy port is correct.
- After any tool call that modifies Unity state, check the Unity console via `mcp_unitymcp_read_console` to confirm no errors occurred.
- Do **not** replace `uv run pytest tests/ -v` — Playwright tests cover live integration; pytest covers unit logic. Both are required.

## Killing a Stuck Server

```powershell
$p = (netstat -ano | Select-String "127.0.0.1:8080\s.*LISTENING" | ForEach-Object { ($_ -split '\s+')[-1] } | Select-Object -First 1)
if ($p) { Stop-Process -Id $p -Force; Write-Host "Killed $p" } else { Write-Host "Not found" }
```
