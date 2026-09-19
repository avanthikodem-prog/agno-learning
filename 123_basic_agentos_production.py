import logging
import os
from pathlib import Path

from agno.agent import Agent
from agno.db.sqlite import SqliteDb
from agno.models.ollama import Ollama
from agno.os import AgentOS


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("basic_agentos_production")


# ============================================================
# CONFIGURATION
# ============================================================

AGENT_OS_ID = "gram-swaram-agentos"
AGENT_ID = "agri-assistant"
AGENT_NAME = "AgriAssistant"

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


# ============================================================
# STORAGE DIRECTORY
# ============================================================

storage_dir = Path("storage")
storage_dir.mkdir(parents=True, exist_ok=True)

database_file = storage_dir / "agentos_production.db"

logger.info(
    "AgentOS storage configured | database=%s",
    database_file,
)


# ============================================================
# DATABASE
# ============================================================

db = SqliteDb(
    id="agentos-production-db",
    db_file=str(database_file),
)

logger.info("SQLite database initialized")


# ============================================================
# OLLAMA MODEL
# ============================================================

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


# ============================================================
# AGENT
# ============================================================

agri_assistant = Agent(
    id=AGENT_ID,
    name=AGENT_NAME,
    model=model,
    db=db,
    instructions=[
        "You are AgriAssistant.",
        "You help users with agriculture-related questions.",
        "Give clear and practical answers.",
        "If you do not know something, say that you are not certain.",
        "Keep answers concise unless the user asks for details.",
    ],
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=3,
    markdown=True,
)

logger.info(
    "Agent created | id=%s | name=%s",
    AGENT_ID,
    AGENT_NAME,
)


# ============================================================
# AGENTOS
# ============================================================

agent_os = AgentOS(
    id=AGENT_OS_ID,
    description=(
        "Production-oriented AgentOS example using "
        "Ollama, SQLite persistence, and Agno."
    ),
    agents=[agri_assistant],
)

app = agent_os.get_app()

logger.info(
    "AgentOS application created | id=%s",
    AGENT_OS_ID,
)


# ============================================================
# STARTUP INFORMATION
# ============================================================

def log_startup_information() -> None:
    """Log important runtime configuration."""

    logger.info("=" * 70)
    logger.info("AgentOS Production Exercise")
    logger.info("=" * 70)

    logger.info("AgentOS ID      : %s", AGENT_OS_ID)
    logger.info("Agent ID        : %s", AGENT_ID)
    logger.info("Agent Name      : %s", AGENT_NAME)
    logger.info("Ollama Model    : %s", OLLAMA_MODEL)
    logger.info("Ollama Host     : %s", OLLAMA_HOST)
    logger.info("Database        : %s", database_file)
    logger.info("Server Host     : %s", AGENT_OS_HOST)
    logger.info("Server Port     : %s", AGENT_OS_PORT)

    logger.info("=" * 70)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    log_startup_information()

    logger.info(
        "Starting AgentOS server | http://%s:%s",
        AGENT_OS_HOST,
        AGENT_OS_PORT,
    )

    logger.info(
        "Configuration endpoint: "
        "http://%s:%s/config",
        AGENT_OS_HOST,
        AGENT_OS_PORT,
    )

    logger.info(
        "Health endpoint: "
        "http://%s:%s/health",
        AGENT_OS_HOST,
        AGENT_OS_PORT,
    )

    logger.info(
        "AgentOS server is ready to accept requests"
    )

    try:

        agent_os.serve(
            app=app,
            host=AGENT_OS_HOST,
            port=AGENT_OS_PORT,
            reload=False,
            access_log=True,
        )

    except KeyboardInterrupt:

        logger.info(
            "AgentOS server stopped by user"
        )

    except Exception:

        logger.exception(
            "AgentOS server stopped because of an unexpected error"
        )

        raise

    finally:

        logger.info(
            "AgentOS server shutdown completed"
        )