from agno.agent import Agent
from agno.models.ollama import Ollama
from pydantic import BaseModel


# -----------------------------------------
# 1. Define the output structure
# -----------------------------------------

class Farmer(BaseModel):
    name: str
    state: str
    crops: list[str]


# -----------------------------------------
# 2. Create the Agent
# -----------------------------------------

agent = Agent(
    name="Farmer Structured Agent",
    model=Ollama(id="llama3.2"),
    output_schema=Farmer,
)


# -----------------------------------------
# 3. Run the Agent
# -----------------------------------------

response = agent.run(
    "Tell me about Ravi, a farmer from Telangana who grows paddy and cotton."
)


# -----------------------------------------
# 4. Access structured data
# -----------------------------------------

farmer = response.content

print("\n========== FARMER DETAILS ==========\n")

print("Name:", farmer.name)
print("State:", farmer.state)
print("Crops:", farmer.crops)
