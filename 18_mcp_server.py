from mcp.server.fastmcp import FastMCP

mcp = FastMCP("GramSwaram MCP Server")


@mcp.tool()
def get_farmer_info(farmer_name: str) -> str:
    """Get information about a farmer."""
    
    farmers = {
        "Ravi": "Ravi is a farmer from Telangana. He grows paddy and cotton.",
        "Suresh": "Suresh is a farmer from Andhra Pradesh. He grows rice and chilli.",
        "Ramesh": "Ramesh is a farmer from Karnataka. He grows sugarcane.",
    }

    return farmers.get(
        farmer_name,
        f"No information found for farmer {farmer_name}."
    )


if __name__ == "__main__":
    mcp.run()