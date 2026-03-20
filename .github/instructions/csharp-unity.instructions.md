---
name: 'C# Unity Editor Package'
description: 'Conventions for the Unity C# Editor plugin (MCPForUnity)'
applyTo: 'MCPForUnity/**/*.cs'
---
# C# Unity Editor Package Conventions

## Tool Registration

Tools are auto-discovered by `CommandRegistry` via reflection. Use the `[McpForUnityTool]` attribute:

```csharp
[McpForUnityTool("manage_something", AutoRegister = false, Group = "core")]
public static class ManageSomething
{
    // Sync handler (most tools):
    public static object HandleCommand(JObject @params)
    {
        var p = new ToolParams(@params);
        var action = p.RequireString("action");
        // ...
        return new SuccessResponse("Done.", new { data = result });
    }

    // OR async handler (for long-running operations):
    public static async Task<object> HandleCommand(JObject @params)
    {
        await SomeAsyncOperation();
        return new SuccessResponse("Done.");
    }
}
```

## Parameter Handling

Use `ToolParams` for consistent parameter access and validation:

```csharp
var p = new ToolParams(parameters);
var pageSize = p.GetInt("page_size", "pageSize") ?? 50;       // optional with default
var name = p.RequireString("name");                             // required, throws if missing
var flag = p.GetBool("include_details", "includeDetails") ?? false;
```

- `ToolParams` accepts both `snake_case` and `camelCase` parameter names.
- Use `RequireString` / `RequireInt` for required params; they throw descriptive errors.
- Use `GetInt` / `GetBool` / `GetString` for optional params; they return `null` if missing.

## Resources

Resources use `[McpForUnityResource]` and follow the same `HandleCommand` pattern as tools. They provide read-only state to AI assistants.

## Paging

Always page results that could be large (hierarchies, components, search results):
- Accept `page_size` and `cursor` parameters.
- Return `next_cursor` when more results exist.
- Default page sizes: hierarchy=50, components=10-25, assets=25-50.

## Internal Tool Composition

Use `CommandRegistry.InvokeCommandAsync` to call other tools from within a handler:

```csharp
var result = await CommandRegistry.InvokeCommandAsync("read_console", consoleParams);
```

## Async Patterns

Async handlers use `EditorApplication.update` polling with `TaskCompletionSource`. See `RefreshUnity.cs` for the canonical pattern. `CommandRegistry` detects `Task` return types automatically.

## Domain Symmetry

Each C# tool mirrors a Python MCP tool:
- `ManageMaterial.cs` ↔ `manage_material.py`
- `ManageScene.cs` ↔ `manage_scene.py`

The C# `HandleCommand` receives the same parameters that the Python tool sends via WebSocket.
