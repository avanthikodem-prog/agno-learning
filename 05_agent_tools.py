from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.calculator import CalculatorTools


# -------------------------
# Tool 1: Calculator
# -------------------------

calculator = CalculatorTools()


# -------------------------
# Tool 2: Weather
# -------------------------

def get_weather(city: str) -> str:
    """Get weather information for a city."""
    weather_data = {
        "Hyderabad": "Sunny, 32°C",
        "Chennai": "Cloudy, 30°C",
        "Delhi": "Clear, 28°C",
    }

    return weather_data.get(
        city,
        f"Weather information for {city} is not available."
    )


# -------------------------
# Tool 3: Farmer Information
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
# Create Agent
# -------------------------

agent = Agent(
    name="Smart Assistant",
    model=Ollama(id="llama3.2"),
    tools=[
        calculator,
        get_weather,
        get_farmer_info,
    ],
    instructions="""
    You are a smart assistant.

    You have access to three tools:

    1. Calculator - use it for mathematical calculations.
    2. get_weather - use it when the user asks about weather.
    3. get_farmer_info - use it when the user asks about a farmer.

    Decide which tool to use based on the user's question.
    If no tool is required, answer directly.
    """,
)


# -------------------------
# Test the Agent
# -------------------------

agent.print_response(
    "What is an AI agent?"
)