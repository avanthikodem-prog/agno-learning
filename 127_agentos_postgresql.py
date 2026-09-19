import logging
import os

from dotenv import load_dotenv

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.models.ollama import Ollama
from agno.os import AgentOS


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agentos_postgresql")


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()

logger.info("Environment variables loaded")


# ---------------------------------------------------------
# Read configuration
# ---------------------------------------------------------

POSTGRES_DB_URL = os.getenv("POSTGRES_DB_URL")

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://127.0.0.1:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2",
)

AGENT_OS_HOST = os.getenv(
    "AGENT_OS_HOST",
    "127.0.0.1",
)

AGENT_OS_PORT = int(
    os.getenv(
        "AGENT_OS_PORT",
        "7777",
    )
)


# ---------------------------------------------------------
# Validate PostgreSQL configuration
# ---------------------------------------------------------

if not POSTGRES_DB_URL:
    raise ValueError(
        "POSTGRES_DB_URL is missing from the .env file"
    )

logger.info("PostgreSQL database URL loaded successfully")


# ---------------------------------------------------------
# Create PostgreSQL database
# ---------------------------------------------------------

logger.info(
    "Initializing PostgreSQL database"
)

db = PostgresDb(
    id="gramswaram-agentos-db",
    db_url=POSTGRES_DB_URL,
)

logger.info(
    "PostgreSQL database initialized | id=%s",
    "gramswaram-agentos-db",
)


# ---------------------------------------------------------
# Configure Ollama
# ---------------------------------------------------------

logger.info(
    "Configuring Ollama | model=%s | host=%s",
    OLLAMA_MODEL,
    OLLAMA_HOST,
)

model = Ollama(
    id=OLLAMA_MODEL,
    host=OLLAMA_HOST,
    api_key=None,
    timeout=120,
)

logger.info("Ollama model configured successfully")


# ---------------------------------------------------------
# Create Agent
# ---------------------------------------------------------

agri_assistant = Agent(
    id="agri-assistant",
    name="AgriAssistant",
    model=model,
    db=db,
    instructions=[
        "You are an agriculture assistant.",
        "Help users with agriculture and farmer-service questions.",
        "Use the current session history when answering follow-up questions.",
        "Give clear and practical answers.",
        "Maintain conversation continuity within a session.",
    ],
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)

logger.info(
    "Agent created | id=%s | name=%s",
    agri_assistant.id,
    agri_assistant.name,
)


# ---------------------------------------------------------
# Create AgentOS
# ---------------------------------------------------------

agent_os = AgentOS(
    id="gram-swaram-postgresql-agentos",
    description="AgentOS with PostgreSQL persistence",
    db=db,
    agents=[
        agri_assistant,
    ],
)

app = agent_os.get_app()

logger.info(
    "AgentOS application created | id=%s",
    agent_os.id,
)


# ---------------------------------------------------------
# PostgreSQL architecture
# ---------------------------------------------------------

logger.info(
    "========== PostgreSQL Architecture =========="
)

logger.info(
    "User → AgentOS → Session → AgriAssistant"
)

logger.info(
    "AgriAssistant → Ollama → Llama 3.2"
)

logger.info(
    "AgentOS → PostgreSQL"
)

logger.info(
    "Sessions and persistent AgentOS data → PostgreSQL"
)

logger.info(
    "PostgreSQL database → Gramswaram database"
)

logger.info(
    "=============================================="
)


# ---------------------------------------------------------
# Production database explanation
# ---------------------------------------------------------

logger.info(
    "========== Production Database =========="
)

logger.info(
    "SQLite was used in previous exercises"
)

logger.info(
    "PostgreSQL is now used as the shared database"
)

logger.info(
    "Database is managed by PostgreSQL server"
)

logger.info(
    "AgentOS can persist data outside the application process"
)

logger.info(
    "=========================================="
)


# ---------------------------------------------------------
# Start AgentOS
# ---------------------------------------------------------

logger.info(
    "Starting AgentOS server | http://%s:%s",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "PostgreSQL-backed AgentOS is ready"
)

logger.info(
    "Health endpoint | http://%s:%s/health",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "Swagger documentation | http://%s:%s/docs",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)


agent_os.serve(
    app=app,
    host=AGENT_OS_HOST,
    port=AGENT_OS_PORT,
    reload=False,
    access_log=True,
)