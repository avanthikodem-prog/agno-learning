import asyncio

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


server_params = StdioServerParameters(
    command="python",
    args=["18_mcp_server.py"],
)


async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:

            await session.initialize()

            tools = await session.list_tools()

            print("\n========== AVAILABLE MCP TOOLS ==========\n")

            for tool in tools.tools:
                print("Tool:", tool.name)
                print("Description:", tool.description)

            print("\n========== CALLING TOOL ==========\n")

            result = await session.call_tool(
                "get_farmer_info",
                arguments={"farmer_name": "Ravi"},
            )

            print(result)


if __name__ == "__main__":
    asyncio.run(main())