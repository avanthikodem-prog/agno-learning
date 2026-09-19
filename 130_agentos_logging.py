import logging
import os
import time
from typing import Any

from dotenv import load_dotenv
from fastapi import Request

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.models.ollama import Ollama
from agno.os import AgentOS


# ============================================================
# Logging Configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agentos_logging")


# ============================================================
# Environment Configuration
# ============================================================

load_dotenv()

logger.info("Environment variables loaded")


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


# ============================================================
# Environment Validation
# ============================================================

if not POSTGRES_DB_URL:
    logger.error("POSTGRES_DB_URL is missing")
    raise ValueError(
        "POSTGRES_DB_URL is missing from .env"
    )

if not OS_SECURITY_KEY:
    logger.error("OS_SECURITY_KEY is missing")
    raise ValueError(
        "OS_SECURITY_KEY is missing from .env"
    )

logger.info("PostgreSQL configuration validated")
logger.info("AgentOS security configuration validated")

# IMPORTANT:
# Never log the actual values of:
# - OS_SECURITY_KEY
# - POSTGRES_DB_URL
# - API_KEY


# ============================================================
# PostgreSQL
# ============================================================

logger.info("Initializing PostgreSQL database")

db = PostgresDb(
    id="gramswaram-agentos-db",
    db_url=POSTGRES_DB_URL,
)

logger.info(
    "PostgreSQL database initialized | id=%s",
    "gramswaram-agentos-db",
)


# ============================================================
# Ollama
# ============================================================

logger.info(
    "Initializing Ollama | model=%s | host=%s",
    OLLAMA_MODEL,
    OLLAMA_HOST,
)

model = Ollama(
    id=OLLAMA_MODEL,
    host=OLLAMA_HOST,
    api_key=None,
    timeout=120,
)

logger.info("Ollama model initialized successfully")


# ============================================================
# Agent
# ============================================================

logger.info("Creating AgriAssistant")

agri_assistant = Agent(
    id="agri-assistant",
    name="AgriAssistant",
    model=model,
    db=db,
    instructions=[
        "You are an agriculture assistant.",
        "Help users with agriculture and farmer-service questions.",
        "Give clear and practical answers.",
        "Use session history when answering follow-up questions.",
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


# ============================================================
# AgentOS
# ============================================================

logger.info("Creating AgentOS")

agent_os = AgentOS(
    id="gram-swaram-logging-agentos",
    description="AgentOS production logging demonstration",
    db=db,
    agents=[agri_assistant],
)

logger.info(
    "AgentOS created | id=%s",
    agent_os.id,
)


# ============================================================
# FastAPI Application
# ============================================================

app = agent_os.get_app()

logger.info("AgentOS FastAPI application created")


# ============================================================
# Request Logging Middleware
# ============================================================

@app.middleware("http")
async def request_logging_middleware(
    request: Request,
    call_next: Any,
):
    """
    Log every incoming HTTP request and its response time.
    """

    start_time = time.perf_counter()

    logger.info(
        "Request started | method=%s | path=%s",
        request.method,
        request.url.path,
    )

    try:
        response = await call_next(request)

        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.info(
            "Request completed | method=%s | path=%s | status=%s | duration_ms=%.2f",
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )

        return response

    except Exception:
        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.exception(
            "Request failed | method=%s | path=%s | duration_ms=%.2f",
            request.method,
            request.url.path,
            duration_ms,
        )

        raise


# ============================================================
# Logging Demonstration Endpoint
# ============================================================

@app.get("/demo/logging")
async def demonstrate_logging() -> dict[str, str]:
    """
    Generate different log levels for demonstration.
    """

    logger.debug(
        "DEBUG log generated | endpoint=/demo/logging"
    )

    logger.info(
        "INFO log generated | endpoint=/demo/logging"
    )

    logger.warning(
        "WARNING log generated | endpoint=/demo/logging"
    )

    return {
        "status": "ok",
        "message": "Logging demonstration completed",
    }


# ============================================================
# Logging Information Endpoint
# ============================================================

@app.get("/demo/logging-info")
async def logging_information() -> dict[str, Any]:
    """
    Return safe logging configuration information.
    """

    logger.info(
        "Logging information endpoint requested"
    )

    return {
        "logging_enabled": True,
        "log_level": "INFO",
        "structured_format": True,
        "request_logging": True,
        "exception_logging": True,
        "secret_logging": False,
    }


# ============================================================
# Production Logging Architecture
# ============================================================

logger.info(
    "========== AgentOS Logging Architecture =========="
)

logger.info("Application startup logging")
logger.info("       ↓")
logger.info("Request lifecycle logging")
logger.info("       ↓")
logger.info("Agent execution logging")
logger.info("       ↓")
logger.info("Database operation logging")
logger.info("       ↓")
logger.info("Authentication logging")
logger.info("       ↓")
logger.info("Exception logging")
logger.info("       ↓")
logger.info("Application shutdown logging")

logger.info(
    "==================================================="
)


# ============================================================
# Security Logging Rules
# ============================================================

logger.info(
    "========== Logging Security Rules =========="
)

logger.info(
    "OS_SECURITY_KEY logging: DISABLED"
)

logger.info(
    "POSTGRES_DB_URL logging: DISABLED"
)

logger.info(
    "API_KEY logging: DISABLED"
)

logger.info(
    "Sensitive request headers logging: DISABLED"
)

logger.info(
    "================================================"
)


# ============================================================
# Startup Information
# ============================================================

logger.info(
    "Starting AgentOS Logging Server"
)

logger.info(
    "Host=%s | Port=%s",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "Health endpoint | http://%s:%s/health",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "Logging demonstration | "
    "http://%s:%s/demo/logging",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "Logging information | "
    "http://%s:%s/demo/logging-info",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "AgentOS logging server is ready"
)


# ============================================================
# Start AgentOS
# ============================================================

if __name__ == "__main__":
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
            "AgentOS shutdown requested by user"
        )

    except Exception:
        logger.exception(
            "AgentOS terminated because of an unexpected error"
        )

    finally:
        logger.info(
            "AgentOS logging server stopped"
        )