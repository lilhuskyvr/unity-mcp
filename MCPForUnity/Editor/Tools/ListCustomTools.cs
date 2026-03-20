using System;
using System.Collections.Generic;
using System.Linq;
using MCPForUnity.Editor.Helpers;
using MCPForUnity.Editor.Services;
using Newtonsoft.Json.Linq;

namespace MCPForUnity.Editor.Tools
{
    /// <summary>
    /// Lists all custom (project-defined) tools registered in this Unity project.
    /// A custom tool is any [McpForUnityTool]-decorated class whose assembly is
    /// not part of the built-in MCPForUnity package.
    ///
    /// This is the tool-callable counterpart of the mcpforunity://custom-tools resource,
    /// allowing AI agents to discover available custom tools without resource protocol support.
    /// </summary>
    [McpForUnityTool("list_custom_tools", AutoRegister = false)]
    public static class ListCustomTools
    {
        public static object HandleCommand(JObject @params)
        {
            try
            {
                var discovery = MCPServiceLocator.ToolDiscovery;
                var allTools = discovery.DiscoverAllTools();

                var customToolsArray = new JArray();
                foreach (var tool in allTools)
                {
                    if (tool.IsBuiltIn)
                        continue;

                    var parametersArray = new JArray();
                    foreach (var param in tool.Parameters)
                    {
                        parametersArray.Add(new JObject
                        {
                            ["name"] = param.Name,
                            ["description"] = param.Description,
                            ["type"] = param.Type,
                            ["required"] = param.Required,
                            ["default_value"] = param.DefaultValue
                        });
                    }

                    customToolsArray.Add(new JObject
                    {
                        ["name"] = tool.Name,
                        ["description"] = tool.Description,
                        ["group"] = tool.Group ?? "core",
                        ["enabled"] = discovery.IsToolEnabled(tool.Name),
                        ["requires_polling"] = tool.RequiresPolling,
                        ["poll_action"] = tool.PollAction,
                        ["parameters"] = parametersArray
                    });
                }

                var result = new JObject
                {
                    ["tools"] = customToolsArray,
                    ["tool_count"] = customToolsArray.Count
                };

                return new SuccessResponse("Custom tools retrieved successfully.", result);
            }
            catch (Exception e)
            {
                return new ErrorResponse($"Failed to retrieve custom tools: {e.Message}");
            }
        }
    }
}
