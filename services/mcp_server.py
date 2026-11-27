"""Local read-only MCP server; exposes only implemented MVP capabilities."""
from mcp.server.fastmcp import FastMCP

from api.main import list_careers as api_list_careers

server = FastMCP("USFQ Schedule")


@server.tool()
def list_careers() -> list[dict[str, str]]:
    """List the two careers supported by the MVP, not curriculum contents."""
    return [career.model_dump() for career in api_list_careers()]


if __name__ == "__main__":
    server.run(transport="stdio")
