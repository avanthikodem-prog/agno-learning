from typing import Literal

from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.models.ollama import Ollama


# --------------------------------------------------
# 1. Structured classification schema
# --------------------------------------------------

class FarmerClassification(BaseModel):
    category: Literal[
        "Crop Problem",
        "Irrigation",
        "Weather",
        "Market",
        "Fertilizer",
        "General Query",
    ] = Field(description="Main category of the farmer's message.")

    type: str = Field(
        description="Specific type of problem or request."
    )

    priority: Literal[
        "Low",
        "Medium",
        "High",
    ] = Field(description="Priority of the farmer's message.")


# --------------------------------------------------
# 2. Classification Agent
# --------------------------------------------------

classification_agent = Agent(
    name="Farmer Classification Agent",
    model=Ollama(id="llama3.2"),
    output_schema=FarmerClassification,
    instructions=[
        "You classify farmer messages into exactly one category.",

        "CATEGORY DEFINITIONS:",

        "Crop Problem: pests, insects, diseases, "
        "yellow leaves, crop damage, plant health problems.",

        "Irrigation: lack of water, no water, "
        "water shortage, irrigation system problems.",

        "Weather: rain, temperature, storms, "
        "weather forecasts, weather conditions.",

        "Market: crop prices, market prices, "
        "selling crops, buyers, market information.",

        "Fertilizer: fertilizer recommendations, "
        "fertilizer usage, nutrients, fertilizer quantity.",

        "General Query: questions that do not belong "
        "to the other categories.",

        "IMPORTANT:",
        "If the farmer says there is NO WATER or WATER SHORTAGE, "
        "the category MUST be Irrigation.",

        "If the farmer asks about FERTILIZER, "
        "the category MUST be Fertilizer.",

        "Examples:",
        "No water is coming to my field -> Irrigation",
        "My crop has insects -> Crop Problem",
        "Will it rain tomorrow? -> Weather",
        "What is the paddy price? -> Market",
        "Which fertilizer should I use? -> Fertilizer",
    ],
)


# --------------------------------------------------
# 3. Routing function
# --------------------------------------------------

def route_farmer_request(classification: FarmerClassification) -> str:

    if classification.category == "Crop Problem":
        return "Route to Crop Support Agent"

    elif classification.category == "Irrigation":
        return "Route to Irrigation Support Agent"

    elif classification.category == "Weather":
        return "Route to Weather Agent"

    elif classification.category == "Market":
        return "Route to Market Information Agent"

    elif classification.category == "Fertilizer":
        return "Route to Fertilizer Support Agent"

    else:
        return "Route to General Support Agent"


# --------------------------------------------------
# 4. Farmer message
# --------------------------------------------------

farmer_message = """
There is no water coming to my field for the last three days.
My rice crop is starting to dry because of the water shortage.
"""


print("=" * 60)
print("AGNO CLASSIFICATION AND ROUTING")
print("=" * 60)


print("\nFarmer Message:")
print(farmer_message)


# --------------------------------------------------
# 5. Classify
# --------------------------------------------------

response = classification_agent.run(
    farmer_message
)

classification = response.content


# --------------------------------------------------
# 6. Display classification
# --------------------------------------------------

print("\n" + "=" * 60)
print("CLASSIFICATION")
print("=" * 60)

print(f"Category: {classification.category}")
print(f"Type: {classification.type}")
print(f"Priority: {classification.priority}")


# --------------------------------------------------
# 7. Route
# --------------------------------------------------

route = route_farmer_request(classification)


print("\n" + "=" * 60)
print("ROUTING")
print("=" * 60)

print(route)