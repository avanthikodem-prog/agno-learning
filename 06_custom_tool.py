from agno.agent import Agent
from agno.models.ollama import Ollama


# -------------------------
# Custom Tool
# -------------------------

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


# -------------------------
# Agent
# -------------------------

agent = Agent(
    name="Farmer Assistant",
    model=Ollama(id="llama3.2"),
    tools=[get_farmer_info],
    instructions="""
    You are a farmer assistant.

    When the user asks about a specific farmer, ALWAYS call
    the get_farmer_info tool.

    After receiving the tool result, answer the user using
    ONLY the information returned by the tool.

    Do not invent, guess, or add any information.
    """
)


# -------------------------
# Test Agent
# -------------------------

agent.print_response(
    "Use the get_farmer_info tool to find information about Ravi."
)