from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.os import AgentOS
from agno.db.sqlite import SqliteDb


# Create the database
db = SqliteDb(
    db_file="sessions.db"
)


# Create the agent
farmer_agent = Agent(
    name="Farmer API Agent",
    model=Ollama(id="llama3.2"),
    instructions="""
    You are a helpful farmer assistant.

    Answer questions about farming and crops
    in a simple and clear way.
    """,
)


# Create AgentOS
agent_os = AgentOS(
    name="GramSwaram Agent Platform",
    agents=[farmer_agent],
    db=db,
    scheduler=True,
    scheduler_poll_interval=15,
    mcp=True,
)


# Get FastAPI application
app = agent_os.get_app()


# Start AgentOS
if __name__ == "__main__":
    agent_os.serve(
        app="17_agent_api:app",
        reload=True,
    )