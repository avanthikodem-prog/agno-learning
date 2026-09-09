from agno.agent import Agent
from agno.models.ollama import Ollama


classification_agent = Agent(
    name="Batch Classification Agent",
    model=Ollama(id="llama3.2"),
    instructions=[
        "You are a farmer message classification agent.",
        "Classify every farmer message.",
        "Use only the provided categories.",
        "Return one classification for each message.",
        "Keep the output clear and structured.",
    ],
)


farmer_messages = [
    "My crop leaves have many insects and are becoming yellow.",
    "There is no water coming to my field for the last three days.",
    "Will there be heavy rain tomorrow?",
    "What is today's market price for paddy?",
    "Which fertilizer should I use for my rice crop?",
]


print("=" * 60)
print("AGNO BATCH DATA CLASSIFICATION")
print("=" * 60)


print("\nFarmer Messages:")

for i, message in enumerate(farmer_messages, start=1):
    print(f"{i}. {message}")


messages_text = "\n".join(
    f"{i}. {message}"
    for i, message in enumerate(farmer_messages, start=1)
)


response = classification_agent.run(
    f"""
Classify all of the following farmer messages.

Available categories:

- Crop Problem
- Irrigation
- Weather
- Market
- Fertilizer
- General Query

For every message provide:

Message Number:
Category:
Type:
Priority:

Priority must be:
- Low
- Medium
- High

Farmer messages:

{messages_text}

Return a classification for EVERY message.
"""
)


print("\n" + "=" * 60)
print("CLASSIFICATION RESULTS")
print("=" * 60)

print(response.content)