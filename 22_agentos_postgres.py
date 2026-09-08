import os

from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.os import AgentOS
from agno.db.postgres import PostgresDb


# Load environment variables
load_dotenv()


# Get PostgreSQL database URL
db_url = os.getenv("POSTGRES_DB_URL")

if not db_url:
    raise ValueError("POSTGRES_DB_URL is not set in .env")


# Create PostgreSQL database
db = PostgresDb(
    db_url=db_url
)


# Create Farmer Agent
farmer_agent = Agent(
    name="GramSwaram Farmer Agent",
    model=Ollama(id="llama3.2"),
    instructions="""
    You are a helpful farmer assistant.

    Answer questions about farming and crops
    in simple and clear language.
    """,
)


# Create AgentOS
agent_os = AgentOS(
    name="GramSwaram AgentOS",
    agents=[farmer_agent],
    db=db,
)


# Get FastAPI application
app = agent_os.get_app()


# Start AgentOS
if __name__ == "__main__":
    agent_os.serve(
        app="22_agentos_postgres:app",
        reload=True,
    )