import logging
import os
from pathlib import Path

from dotenv import load_dotenv

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.ollama import Ollama
from agno.os import AgentOS


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agentos_sessions")


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()

logger.info("Environment variables loaded")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

OLLAMA_HOST = os.getenv(
    "OLLAMA_HOST",
    "http://127.0.0.1:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "llama3.2",
)

DATABASE_PATH = os.getenv(
    "AGENTOS_DB_PATH",
    "storage/agentos_sessions.db",
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
# Prepare storage
# ---------------------------------------------------------

database_file = Path(DATABASE_PATH)

database_file.parent.mkdir(
    parents=True,
    exist_ok=True,
)

logger.info(
    "Session database configured | path=%s",
    database_file,
)


# ---------------------------------------------------------
# SQLite database
# ---------------------------------------------------------

db = SqliteDb(
    db_file=str(database_file),
)

logger.info("SQLite database initialized")


# ---------------------------------------------------------
# Ollama model
# ---------------------------------------------------------

model = Ollama(
    id=OLLAMA_MODEL,
    host=OLLAMA_HOST,
    api_key=None,
    timeout=120,
)

logger.info(
    "Ollama model configured | model=%s | host=%s",
    OLLAMA_MODEL,
    OLLAMA_HOST,
)


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
        "Remember the conversation context within the current session.",
        "Give clear and practical answers.",
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
    id="gram-swaram-session-agentos",
    description="AgentOS session management example",
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
# Session concepts
# ---------------------------------------------------------

logger.info("Preparing session demonstration")

logger.info(
    "Session A represents one user's conversation"
)

logger.info(
    "Session B represents another user's conversation"
)

logger.info(
    "Each session has an independent session identifier"
)

logger.info(
    "Conversation history is associated with the session"
)


# ---------------------------------------------------------
# Session lifecycle explanation
# ---------------------------------------------------------

logger.info("========== Session Lifecycle ==========")

logger.info("1. Session created")
logger.info("2. User sends a message")
logger.info("3. Agent processes the message")
logger.info("4. Conversation state is stored")
logger.info("5. User sends another message")
logger.info("6. Agent retrieves session history")
logger.info("7. Agent continues the conversation")

logger.info("=======================================")


# ---------------------------------------------------------
# Production session architecture
# ---------------------------------------------------------

logger.info("========== Session Architecture ==========")

logger.info(
    "User → AgentOS → Session → Agent → Ollama"
)

logger.info(
    "Session → SQLite database"
)

logger.info(
    "Session history → Retrieved for future requests"
)

logger.info(
    "Multiple users → Separate sessions"
)

logger.info("===========================================")


# ---------------------------------------------------------
# Start AgentOS
# ---------------------------------------------------------

logger.info(
    "Starting AgentOS server | http://%s:%s",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "Sessions API available through AgentOS"
)

logger.info(
    "Swagger documentation | http://%s:%s/docs",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "Health endpoint | http://%s:%s/health",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "AgentOS session server is ready"
)


agent_os.serve(
    app=app,
    host=AGENT_OS_HOST,
    port=AGENT_OS_PORT,
    reload=False,
    access_log=True,
)