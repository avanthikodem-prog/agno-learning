from agno.agent import Agent
from agno.models.ollama import Ollama


agent = Agent(
    name="Observable Farmer Agent",
    model=Ollama(id="llama3.2"),
    debug_mode=True,
    instructions="""
    You are a helpful farmer assistant.

    Answer questions about farming and crops
    in a simple and clear way.
    """,
)


response = agent.run(
    "What are the benefits of drip irrigation?"
)


print("\n========== FINAL RESPONSE ==========\n")
print(response.content)

print("\n========== RUN INFORMATION ==========\n")
print("Run ID:", response.run_id)
print("Session ID:", response.session_id)