from agno.agent import Agent
from agno.models.ollama import Ollama


classification_agent = Agent(
    name="Data Classification Agent",
    model=Ollama(id="llama3.2"),
    instructions=[
        "You are a data classification agent.",
        "Classify farmer messages into the correct category.",
        "Identify the type of problem.",
        "Assign a priority: Low, Medium, or High.",
        "Always use exactly this format:",
        "Category: ...",
        "Type: ...",
        "Priority: ...",
        "Do not add extra explanations.",
    ],
)


print("=" * 60)
print("AGNO DATA LABELING & CLASSIFICATION")
print("=" * 60)


farmer_message = """
My crop leaves are turning yellow and I can see many small insects
on the leaves. The crop growth is also becoming weak.
"""


print("\nFarmer Message:")
print(farmer_message)


response = classification_agent.run(
    f"""
Classify the following farmer message.

Farmer message:
{farmer_message}

Choose the most appropriate:

Category:
- Crop Problem
- Irrigation
- Weather
- Market
- Fertilizer
- General Query

Type:
Describe the specific type of issue.

Priority:
- Low
- Medium
- High

Return ONLY:

Category: ...
Type: ...
Priority: ...
"""
)


print("\nClassification Result:")
print(response.content)