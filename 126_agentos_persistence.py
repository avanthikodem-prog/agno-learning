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

logger = logging.getLogger("agentos_persistence")


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
    "storage/agentos_production.db",
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
# Prepare persistent storage
# ---------------------------------------------------------

database_file = Path(DATABASE_PATH)

database_file.parent.mkdir(
    parents=True,
    exist_ok=True,
)

logger.info(
    "Persistent storage configured | path=%s",
    database_file,
)


# ---------------------------------------------------------
# Verify existing database
# ---------------------------------------------------------

if database_file.exists():
    logger.info(
        "Existing database found | path=%s | size=%d bytes",
        database_file,
        database_file.stat().st_size,
    )
else:
    logger.info(
        "Database does not exist yet | AgentOS will create it"
    )


# ---------------------------------------------------------
# Create SQLite database
# ---------------------------------------------------------

db = SqliteDb(
    db_file=str(database_file),
)

logger.info(
    "SQLite persistence initialized | database=%s",
    database_file,
)


# ---------------------------------------------------------
# Configure Ollama
# ---------------------------------------------------------

model = Ollama(
    id=OLLAMA_MODEL,
    host=OLLAMA_HOST,
    api_key=None,
    timeout=120,
)

logger.info(
    "Ollama configured | model=%s | host=%s",
    OLLAMA_MODEL,
    OLLAMA_HOST,
)


# ---------------------------------------------------------
# Create persistent Agent
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
        "Provide clear and practical answers.",
        "Maintain conversation continuity within a session.",
    ],
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=5,
    markdown=True,
)

logger.info(
    "Persistent agent created | id=%s | name=%s",
    agri_assistant.id,
    agri_assistant.name,
)


# ---------------------------------------------------------
# Create AgentOS
# ---------------------------------------------------------

agent_os = AgentOS(
    id="gram-swaram-persistence-agentos",
    description="AgentOS persistence demonstration",
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
# Persistence architecture
# ---------------------------------------------------------

logger.info("========== Persistence Architecture ==========")

logger.info(
    "AgentOS → Agent → Session"
)

logger.info(
    "Session → SQLite database"
)

logger.info(
    "SQLite database → Persistent disk storage"
)

logger.info(
    "Server restart → Database remains available"
)

logger.info(
    "New server process → Existing database can be reused"
)

logger.info("==============================================")


# ---------------------------------------------------------
# Persistence lifecycle
# ---------------------------------------------------------

logger.info("========== Persistence Lifecycle ==========")

logger.info(
    "1. User creates or uses a session"
)

logger.info(
    "2. Agent processes the request"
)

logger.info(
    "3. Session information is stored in SQLite"
)

logger.info(
    "4. AgentOS server is stopped"
)

logger.info(
    "5. SQLite database remains on disk"
)

logger.info(
    "6. AgentOS server starts again"
)

logger.info(
    "7. Existing persistent data can be reused"
)

logger.info("===========================================")


# ---------------------------------------------------------
# Persistence safety information
# ---------------------------------------------------------

logger.info(
    "Persistence database file exists=%s",
    database_file.exists(),
)

logger.info(
    "Persistence database path=%s",
    database_file,
)


# ---------------------------------------------------------
# Start AgentOS
# ---------------------------------------------------------

logger.info(
    "Starting AgentOS persistence server | http://%s:%s",
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
    "Persistent AgentOS server is ready"
)


agent_os.serve(
    app=app,
    host=AGENT_OS_HOST,
    port=AGENT_OS_PORT,
    reload=False,
    access_log=True,
)