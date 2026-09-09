from typing import Literal

from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================
# 1. STRUCTURED CLASSIFICATION SCHEMA
# ============================================================

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


# ============================================================
# 2. CLASSIFICATION AGENT
# ============================================================

classification_agent = Agent(
    name="GramSwaram Farmer Classification Agent",
    model=Ollama(id="llama3.2"),
    output_schema=FarmerClassification,
    instructions=[
        "You classify farmer messages into exactly one category.",

        "CATEGORY DEFINITIONS:",

        "Crop Problem: pests, insects, diseases, "
        "yellow leaves, crop damage, plant health problems.",

        "Irrigation: lack of water, no water, "
        "water shortage, irrigation problems.",

        "Weather: rain, temperature, storms, "
        "weather forecasts, weather conditions.",

        "Market: crop prices, market prices, "
        "selling crops, buyers, market information.",

        "Fertilizer: fertilizer recommendations, "
        "fertilizer usage, nutrients, fertilizer quantity.",

        "General Query: questions that do not belong "
        "to the other categories.",

        "IMPORTANT RULES:",

        "If the farmer mentions NO WATER or WATER SHORTAGE, "
        "the category MUST be Irrigation.",

        "If the farmer mentions INSECTS, PESTS, DISEASES, "
        "or YELLOW LEAVES, the category MUST be Crop Problem.",

        "If the farmer asks about RAIN or WEATHER, "
        "the category MUST be Weather.",

        "If the farmer asks about CROP PRICE or MARKET PRICE, "
        "the category MUST be Market.",

        "If the farmer asks which FERTILIZER to use, "
        "the category MUST be Fertilizer.",

        "Examples:",

        "My crop has insects -> Crop Problem",
        "My crop leaves are yellow -> Crop Problem",
        "There is no water in my field -> Irrigation",
        "There is a water shortage -> Irrigation",
        "Will it rain tomorrow? -> Weather",
        "What is the paddy price? -> Market",
        "Which fertilizer should I use? -> Fertilizer",

        "Give a specific and meaningful type.",
        "Choose priority as Low, Medium, or High.",
    ],
)


# ============================================================
# 3. ROUTING FUNCTION
# ============================================================

def route_farmer_request(
    classification: FarmerClassification
) -> str:

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


# ============================================================
# 4. FARMER MESSAGES
# ============================================================

farmer_messages = [
    "My rice crop has many insects and the leaves are turning yellow.",

    "There has been no water in my field for the last three days.",

    "Will there be heavy rain tomorrow?",

    "What is today's market price for paddy?",

    "Which fertilizer should I use for my rice crop?",
]


# ============================================================
# 5. HEADER
# ============================================================

print("=" * 70)
print("GRAMSWARAM - FINAL DATA CLASSIFICATION AND ROUTING")
print("=" * 70)


# ============================================================
# 6. DISPLAY FARMER MESSAGES
# ============================================================

print("\nFARMER MESSAGES")
print("=" * 70)

for i, message in enumerate(farmer_messages, start=1):
    print(f"{i}. {message}")


# ============================================================
# 7. CLASSIFY AND ROUTE EACH MESSAGE
# ============================================================

print("\n" + "=" * 70)
print("CLASSIFICATION AND ROUTING RESULTS")
print("=" * 70)


for i, farmer_message in enumerate(farmer_messages, start=1):

    # --------------------------------------------------------
    # Ask the AI agent to classify the message
    # --------------------------------------------------------

    response = classification_agent.run(
        farmer_message
    )

    classification = response.content

    # --------------------------------------------------------
    # Route based on classification
    # --------------------------------------------------------

    route = route_farmer_request(classification)

    # --------------------------------------------------------
    # Display result
    # --------------------------------------------------------

    print(f"\nMESSAGE {i}")
    print("-" * 70)

    print(f"Farmer Message: {farmer_message}")
    print(f"Category: {classification.category}")
    print(f"Type: {classification.type}")
    print(f"Priority: {classification.priority}")
    print(f"Route: {route}")


# ============================================================
# 8. COMPLETED
# ============================================================

print("\n" + "=" * 70)
print("DATA CLASSIFICATION AND ROUTING COMPLETED")
print("=" * 70)