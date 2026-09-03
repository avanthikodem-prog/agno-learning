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

    Use the get_farmer_info tool whenever
    the user asks about a specific farmer.
    """,
)


# -------------------------
# Test
# -------------------------

agent.print_response(
    "Tell me about farmer Ravi."
)
