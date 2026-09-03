from agno.agent import Agent
from agno.models.ollama import Ollama


agent = Agent(
    model=Ollama(id="llama3.2"),
)

agent.print_response(
    "Explain what Ollama is and how it works with Agno."
)