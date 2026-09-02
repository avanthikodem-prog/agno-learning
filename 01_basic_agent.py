from agno.agent import Agent
from agno.models.ollama import Ollama

agent = Agent(
    model=Ollama(id="llama3.2"),
)

agent.print_response(
    "What is an AI agent? Explain in simple words."
)