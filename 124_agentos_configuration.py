import logging
import os
from dataclasses import dataclass
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

logger = logging.getLogger("agentos_configuration")


# ---------------------------------------------------------
# Load environment variables
# ---------------------------------------------------------

load_dotenv()

logger.info("Environment variables loaded from .env")


# ---------------------------------------------------------
# AgentOS Configuration
# ---------------------------------------------------------

@dataclass(frozen=True)
class AgentOSConfig:
    """
    Central configuration for the AgentOS application.
    """

    ollama_host: str
    ollama_model: str

    agent_os_host: str
    agent_os_port: int

    database_path: str
    environment: str

    @classmethod
    def from_environment(cls):
        """Create configuration from environment variables."""

        ollama_host = os.getenv(
            "OLLAMA_HOST",
            "http://127.0.0.1:11434",
        )

        ollama_model = os.getenv(
            "OLLAMA_MODEL",
            "llama3.2",
        )

        agent_os_host = os.getenv(
            "AGENT_OS_HOST",
            "127.0.0.1",
        )

        port_value = os.getenv(
            "AGENT_OS_PORT",
            "7777",
        )

        database_path = os.getenv(
            "AGENTOS_DB_PATH",
            "storage/agentos_production.db",
        )

        environment = os.getenv(
            "AGENT_OS_ENV",
            "development",
        )

        try:
            agent_os_port = int(port_value)
        except ValueError as exc:
            raise ValueError(
                f"AGENT_OS_PORT must be an integer, got: {port_value}"
            ) from exc

        config = cls(
            ollama_host=ollama_host,
            ollama_model=ollama_model,
            agent_os_host=agent_os_host,
            agent_os_port=agent_os_port,
            database_path=database_path,
            environment=environment,
        )

        return config

    def validate(self):
        """Validate the AgentOS configuration."""

        logger.info("Validating AgentOS configuration")

        if not self.ollama_host:
            raise ValueError("OLLAMA_HOST cannot be empty")

        if not self.ollama_model:
            raise ValueError("OLLAMA_MODEL cannot be empty")

        if not self.agent_os_host:
            raise ValueError("AGENT_OS_HOST cannot be empty")

        if not 1 <= self.agent_os_port <= 65535:
            raise ValueError(
                "AGENT_OS_PORT must be between 1 and 65535"
            )

        if not self.database_path:
            raise ValueError("AGENTOS_DB_PATH cannot be empty")

        if not self.environment:
            raise ValueError("AGENT_OS_ENV cannot be empty")

        logger.info("AgentOS configuration validation successful")

    def prepare_storage(self):
        """Create the database directory if required."""

        database_file = Path(self.database_path)

        if database_file.parent != Path("."):
            database_file.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

        logger.info(
            "Storage directory ready | path=%s",
            database_file.parent,
        )

    def display(self):
        """Display safe configuration information."""

        logger.info("========== AgentOS Configuration ==========")
        logger.info(
            "Environment | %s",
            self.environment,
        )
        logger.info(
            "Ollama host | %s",
            self.ollama_host,
        )
        logger.info(
            "Ollama model | %s",
            self.ollama_model,
        )
        logger.info(
            "AgentOS host | %s",
            self.agent_os_host,
        )
        logger.info(
            "AgentOS port | %s",
            self.agent_os_port,
        )
        logger.info(
            "Database path | %s",
            self.database_path,
        )
        logger.info("============================================")


# ---------------------------------------------------------
# Create AgentOS configuration
# ---------------------------------------------------------

config = AgentOSConfig.from_environment()

config.validate()
config.prepare_storage()
config.display()


# ---------------------------------------------------------
# SQLite database
# ---------------------------------------------------------

logger.info(
    "Initializing SQLite database | path=%s",
    config.database_path,
)

db = SqliteDb(
    db_file=config.database_path,
)

logger.info("SQLite database initialized")


# ---------------------------------------------------------
# Ollama model
# ---------------------------------------------------------

logger.info(
    "Configuring Ollama | model=%s | host=%s",
    config.ollama_model,
    config.ollama_host,
)

model = Ollama(
    id=config.ollama_model,
    host=config.ollama_host,
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
        "Give clear and practical answers.",
    ],
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=3,
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
    id="gram-swaram-agentos",
    description="Production-style AgentOS configuration example",
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
# Start AgentOS
# ---------------------------------------------------------

logger.info(
    "Starting AgentOS server | http://%s:%s",
    config.agent_os_host,
    config.agent_os_port,
)

logger.info(
    "Environment | %s",
    config.environment,
)

logger.info(
    "Health endpoint | http://%s:%s/health",
    config.agent_os_host,
    config.agent_os_port,
)

logger.info(
    "Configuration endpoint | http://%s:%s/config",
    config.agent_os_host,
    config.agent_os_port,
)

logger.info("AgentOS server is ready to accept requests")


agent_os.serve(
    app=app,
    host=config.agent_os_host,
    port=config.agent_os_port,
    reload=False,
    access_log=True,
)