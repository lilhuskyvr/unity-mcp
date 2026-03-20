from fastmcp import Context
from mcp.types import ToolAnnotations

from services.registry import mcp_for_unity_tool


@mcp_for_unity_tool(
    name="dummy_tool",
    description="A dummy tool that returns 'dummy'. For testing purposes only.",
    unity_target=None,
    group=None,
    annotations=ToolAnnotations(
        title="Dummy Tool",
        readOnlyHint=True,
    ),
)
async def dummy_tool(ctx: Context) -> dict:
    await ctx.info("dummy")
    return {"success": True, "message": "dummy"}
