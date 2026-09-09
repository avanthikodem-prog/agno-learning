from typing import Literal

from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.models.ollama import Ollama


# --------------------------------------------------
# 1. Define the structure of the classification
# --------------------------------------------------

class FarmerClassification(BaseModel):
    category: Literal[
        "Crop Problem",
        "Irrigation",
        "Weather",
        "Market",
        "Fertilizer",
        "General Query",
    ] = Field(description="The main category of the farmer's message.")

    type: str = Field(
        description="The specific type of problem or request."
    )

    priority: Literal[
        "Low",
        "Medium",
        "High",
    ] = Field(description="The priority of the farmer's message.")


# --------------------------------------------------
# 2. Create the Agno Agent
# --------------------------------------------------

classification_agent = Agent(
    name="Structured Classification Agent",
    model=Ollama(id="llama3.2"),
    output_schema=FarmerClassification,
    instructions=[
        "You are a farmer message classification agent.",
        "Classify the farmer message accurately.",
        "Use only the allowed category values.",
        "Use only Low, Medium, or High for priority.",
        "Give a specific type for the farmer's request.",
    ],
)


# --------------------------------------------------
# 3. Farmer message
# --------------------------------------------------

farmer_message = """
My rice crop has many insects on the leaves.
The leaves are turning yellow and the crop is becoming weak.
"""


print("=" * 60)
print("AGNO STRUCTURED DATA CLASSIFICATION")
print("=" * 60)


print("\nFarmer Message:")
print(farmer_message)


# --------------------------------------------------
# 4. Run the agent
# --------------------------------------------------

response = classification_agent.run(
    farmer_message
)


# --------------------------------------------------
# 5. Display structured result
# --------------------------------------------------

print("\n" + "=" * 60)
print("STRUCTURED CLASSIFICATION")
print("=" * 60)

classification = response.content

print(f"Category: {classification.category}")
print(f"Type: {classification.type}")
print(f"Priority: {classification.priority}")