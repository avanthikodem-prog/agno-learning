import logging
import os
from typing import Any

from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import JSONResponse

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

logger = logging.getLogger("agentos_error_handling")


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
# Ollama Model
# ============================================================

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


# ============================================================
# Agent
# ============================================================

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
    id="gram-swaram-error-handling-agentos",
    description="AgentOS error handling demonstration",
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
# Global Exception Handler
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Catch unexpected application errors and return
    a safe JSON response instead of exposing internals.
    """

    logger.exception(
        "Unhandled application error | method=%s | path=%s | error=%s",
        request.method,
        request.url.path,
        str(exc),
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected server error occurred.",
            "path": request.url.path,
        },
    )


# ============================================================
# Controlled Error Demonstration Endpoint
# ============================================================

@app.get("/demo/error")
async def demonstrate_error() -> dict[str, Any]:
    """
    Intentionally raise an exception so that Exercise 129
    can demonstrate centralized error handling.
    """

    logger.warning(
        "Intentional error endpoint called for demonstration"
    )

    raise RuntimeError(
        "Intentional demonstration error"
    )


# ============================================================
# Controlled Validation Error Demonstration
# ============================================================

@app.get("/demo/validation-error")
async def demonstrate_validation_error() -> JSONResponse:
    """
    Demonstrate a controlled client-side error response.
    """

    logger.warning(
        "Validation error demonstration endpoint called"
    )

    return JSONResponse(
        status_code=400,
        content={
            "error": "validation_error",
            "message": "The request contains invalid data.",
        },
    )


# ============================================================
# Error Handling Architecture
# ============================================================

logger.info(
    "========== AgentOS Error Handling Architecture =========="
)
logger.info("Client request")
logger.info("       ↓")
logger.info("FastAPI / AgentOS")
logger.info("       ↓")
logger.info("Route execution")
logger.info("       ↓")
logger.info("Exception detected")
logger.info("       ↓")
logger.info("Global exception handler")
logger.info("       ↓")
logger.info("Structured error response")
logger.info("       ↓")
logger.info("Client")
logger.info(
    "=========================================================="
)


# ============================================================
# Production Error Handling Configuration
# ============================================================

logger.info(
    "========== Error Handling Configuration =========="
)
logger.info(
    "Global exception handler: ENABLED"
)
logger.info(
    "Safe JSON error responses: ENABLED"
)
logger.info(
    "Internal exception details exposed to client: NO"
)
logger.info(
    "Exception logging: ENABLED"
)
logger.info(
    "Intentional error test endpoint: /demo/error"
)
logger.info(
    "Validation error test endpoint: /demo/validation-error"
)
logger.info(
    "================================================="
)


# ============================================================
# Start AgentOS
# ============================================================

logger.info(
    "Starting AgentOS | http://%s:%s",
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
    "Error demonstration endpoint | "
    "http://%s:%s/demo/error",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info("AgentOS error handling server is ready")


if __name__ == "__main__":
    agent_os.serve(
        app=app,
        host=AGENT_OS_HOST,
        port=AGENT_OS_PORT,
        reload=False,
        access_log=True,
    )