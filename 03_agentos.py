from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.os import AgentOS


agent = Agent(
    name="Ollama Assistant",
    model=Ollama(id="llama3.2"),
    instructions="You are a helpful AI assistant.",
)


agent_os = AgentOS(
    name="My Agno AgentOS",
    agents=[agent],
)


app = agent_os.get_app()


if __name__ == "__main__":
    agent_os.serve(
        app="03_agentos:app",
        reload=True,
    )