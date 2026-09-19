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

logger = logging.getLogger("agentos_authentication")


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

OS_SECURITY_KEY = os.getenv("OS_SECURITY_KEY")


# ---------------------------------------------------------
# Validate configuration
# ---------------------------------------------------------

if not POSTGRES_DB_URL:
    raise ValueError(
        "POSTGRES_DB_URL is missing from .env"
    )

if not OS_SECURITY_KEY:
    raise ValueError(
        "OS_SECURITY_KEY is missing from .env"
    )

logger.info("PostgreSQL configuration validated")
logger.info("AgentOS security key configuration validated")


# ---------------------------------------------------------
# PostgreSQL database
# ---------------------------------------------------------

logger.info("Initializing PostgreSQL database")

db = PostgresDb(
    id="gramswaram-agentos-db",
    db_url=POSTGRES_DB_URL,
)

logger.info(
    "PostgreSQL database initialized | id=%s",
    "gramswaram-agentos-db",
)


# ---------------------------------------------------------
# Ollama model
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
        "Use session history when answering follow-up questions.",
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
#
# IMPORTANT:
# AgentOS reads OS_SECURITY_KEY automatically
# from the environment.
#
# We DO NOT pass security_key= to AgentOS().
# ---------------------------------------------------------

logger.info(
    "Creating authenticated AgentOS"
)

agent_os = AgentOS(
    id="gram-swaram-auth-agentos",
    description="AgentOS authentication demonstration",
    db=db,
    agents=[
        agri_assistant,
    ],
)

logger.info(
    "AgentOS authentication configured through OS_SECURITY_KEY"
)

app = agent_os.get_app()

logger.info(
    "AgentOS application created | id=%s",
    agent_os.id,
)


# ---------------------------------------------------------
# Authentication architecture
# ---------------------------------------------------------

logger.info(
    "========== Authentication Architecture =========="
)

logger.info(
    "Client"
)

logger.info(
    "   ↓"
)

logger.info(
    "Authorization: Bearer <OS_SECURITY_KEY>"
)

logger.info(
    "   ↓"
)

logger.info(
    "AgentOS authentication"
)

logger.info(
    "   ↓"
)

logger.info(
    "Protected AgentOS API"
)

logger.info(
    "   ↓"
)

logger.info(
    "AgriAssistant"
)

logger.info(
    "=================================================="
)


# ---------------------------------------------------------
# Security information
# ---------------------------------------------------------

logger.info(
    "========== Security Configuration =========="
)

logger.info(
    "Authentication mode: security_key"
)

logger.info(
    "OS_SECURITY_KEY is configured"
)

logger.info(
    "Security key value is intentionally not logged"
)

logger.info(
    "Protected API requests require Bearer authentication"
)

logger.info(
    "============================================"
)


# ---------------------------------------------------------
# Start AgentOS
# ---------------------------------------------------------

logger.info(
    "Starting authenticated AgentOS | http://%s:%s",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
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

logger.info(
    "Authenticated AgentOS server is ready"
)


agent_os.serve(
    app=app,
    host=AGENT_OS_HOST,
    port=AGENT_OS_PORT,
    reload=False,
    access_log=True,
)