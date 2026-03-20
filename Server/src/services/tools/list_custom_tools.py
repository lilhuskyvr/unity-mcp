from fastmcp import Context
from mcp.types import ToolAnnotations
from models.models import MCPResponse

from services.custom_tool_service import (
    get_user_id_from_context,
    resolve_project_id_for_unity_instance,
)
from services.registry import mcp_for_unity_tool
from services.tools import get_unity_instance_from_context
from transport.unity_transport import send_with_unity_instance
from transport.legacy.unity_connection import async_send_command_with_retry


@mcp_for_unity_tool(
    name="list_custom_tools",
    unity_target=None,
    group=None,
    description="List all custom (project-defined) tools registered in the active Unity project. Call this before execute_custom_tool to discover available tool names and their parameters.",
    annotations=ToolAnnotations(
        title="List Custom Tools",
        readOnlyHint=True,
    ),
)
async def list_custom_tools(ctx: Context) -> MCPResponse:
    unity_instance = await get_unity_instance_from_context(ctx)
    if not unity_instance:
        return MCPResponse(
            success=False,
            message="No active Unity instance. Call set_active_instance with Name@hash from mcpforunity://instances.",
        )

    project_id = resolve_project_id_for_unity_instance(unity_instance)
    if project_id is None:
        return MCPResponse(
            success=False,
            message=f"Could not resolve project id for {unity_instance}. Ensure Unity is running and reachable.",
        )

    user_id = await get_user_id_from_context(ctx)
    response = await send_with_unity_instance(
        async_send_command_with_retry,
        unity_instance,
        "list_custom_tools",
        {},
        user_id=user_id,
    )

    if not isinstance(response, dict):
        return MCPResponse(
            success=False,
            message="Unexpected response from Unity.",
        )

    success = response.get("success", False)
    message = response.get("message", "")
    data = response.get("data")

    return MCPResponse(
        success=success,
        message=message,
        data=data,
    )
