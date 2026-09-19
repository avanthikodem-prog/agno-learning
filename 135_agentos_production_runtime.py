import logging
import os
import signal
import time
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import Request
from fastapi.responses import JSONResponse

from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.models.ollama import Ollama
from agno.os import AgentOS


# ============================================================
# Logging
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agentos_production_runtime")


# ============================================================
# Environment
# ============================================================

load_dotenv()

POSTGRES_DB_URL = os.getenv("POSTGRES_DB_URL")
OS_SECURITY_KEY = os.getenv("OS_SECURITY_KEY")

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

AGENT_OS_ENV = os.getenv(
    "AGENT_OS_ENV",
    "development",
)


# ============================================================
# Configuration validation
# ============================================================

if not POSTGRES_DB_URL:
    raise RuntimeError(
        "POSTGRES_DB_URL is not configured"
    )

if not OS_SECURITY_KEY:
    raise RuntimeError(
        "OS_SECURITY_KEY is not configured"
    )


logger.info(
    "Production runtime configuration loaded"
)

logger.info(
    "Runtime environment | environment=%s",
    AGENT_OS_ENV,
)

logger.info(
    "Runtime server | host=%s | port=%s",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "Runtime LLM | provider=Ollama | model=%s",
    OLLAMA_MODEL,
)


# ============================================================
# Runtime state
# ============================================================

runtime_started_at = datetime.now(
    timezone.utc
)

runtime_start_monotonic = time.perf_counter()

shutdown_requested = False

runtime_lock = Lock()


# ============================================================
# PostgreSQL
# ============================================================

db = PostgresDb(
    id="gramswaram-agentos-db",
    db_url=POSTGRES_DB_URL,
)

logger.info(
    "PostgreSQL configured | database_id=%s",
    "gramswaram-agentos-db",
)


# ============================================================
# Ollama
# ============================================================

model = Ollama(
    id=OLLAMA_MODEL,
    host=OLLAMA_HOST,
    api_key=None,
    timeout=120,
)

logger.info(
    "Ollama configured | host=%s | model=%s",
    OLLAMA_HOST,
    OLLAMA_MODEL,
)


# ============================================================
# Agent
# ============================================================

agri_assistant = Agent(
    id="agri-assistant",
    name="AgriAssistant",
    model=model,
    db=db,
    instructions=[
        "You are an AI assistant for agriculture and farmer services.",
        "Give concise and useful answers.",
        "Do not expose secrets or internal configuration.",
    ],
    add_datetime_to_context=True,
    add_history_to_context=True,
    num_history_runs=3,
    markdown=True,
)

logger.info(
    "Agent initialized | id=%s",
    agri_assistant.id,
)


# ============================================================
# AgentOS
# ============================================================

agent_os = AgentOS(
    id="gram-swaram-production-runtime-agentos",
    description="AgentOS production runtime demonstration",
    db=db,
    agents=[agri_assistant],
)

app = agent_os.get_app()

logger.info(
    "AgentOS application created | id=%s",
    "gram-swaram-production-runtime-agentos",
)


# ============================================================
# Startup / shutdown lifecycle
# ============================================================

@app.on_event("startup")
async def startup_event():

    global runtime_started_at
    global runtime_start_monotonic
    global shutdown_requested

    with runtime_lock:
        runtime_started_at = datetime.now(
            timezone.utc
        )

        runtime_start_monotonic = (
            time.perf_counter()
        )

        shutdown_requested = False

    logger.info(
        "AgentOS production runtime STARTED"
    )

    logger.info(
        "Startup lifecycle completed successfully"
    )


@app.on_event("shutdown")
async def shutdown_event():

    global shutdown_requested

    with runtime_lock:
        shutdown_requested = True

    uptime_seconds = (
        time.perf_counter()
        - runtime_start_monotonic
    )

    logger.info(
        "AgentOS production runtime SHUTDOWN requested"
    )

    logger.info(
        "Runtime uptime before shutdown | seconds=%.2f",
        uptime_seconds,
    )

    logger.info(
        "Shutdown lifecycle completed"
    )


# ============================================================
# Runtime status
# ============================================================

@app.get("/demo/runtime-status")
async def runtime_status() -> Dict[str, Any]:

    with runtime_lock:
        current_shutdown_state = shutdown_requested
        started_at = runtime_started_at

    uptime_seconds = (
        time.perf_counter()
        - runtime_start_monotonic
    )

    return {
        "service": "AgentOS",
        "runtime_status": (
            "stopping"
            if current_shutdown_state
            else "running"
        ),
        "environment": AGENT_OS_ENV,
        "started_at": started_at.isoformat(),
        "uptime_seconds": round(
            uptime_seconds,
            2,
        ),
        "shutdown_requested": current_shutdown_state,
        "host": AGENT_OS_HOST,
        "port": AGENT_OS_PORT,
        "llm_provider": "Ollama",
        "llm_model": OLLAMA_MODEL,
        "database": "PostgreSQL",
    }


# ============================================================
# Runtime configuration
# ============================================================

@app.get("/demo/runtime-config")
async def runtime_config():

    return {
        "service": "AgentOS",
        "environment": AGENT_OS_ENV,
        "host": AGENT_OS_HOST,
        "port": AGENT_OS_PORT,
        "reload": False,
        "access_log": True,
        "database": "PostgreSQL",
        "llm_provider": "Ollama",
        "llm_model": OLLAMA_MODEL,
        "authentication": "security_key",
        "secrets_exposed": False,
    }


# ============================================================
# Runtime readiness
# ============================================================

@app.get("/demo/runtime-readiness")
async def runtime_readiness():

    with runtime_lock:
        is_stopping = shutdown_requested

    if is_stopping:

        return JSONResponse(
            status_code=503,
            content={
                "ready": False,
                "status": "stopping",
                "message": (
                    "AgentOS runtime is shutting down."
                ),
            },
        )

    return {
        "ready": True,
        "status": "running",
        "message": (
            "AgentOS runtime is ready to accept requests."
        ),
    }


# ============================================================
# Runtime information
# ============================================================

@app.get("/demo/runtime-info")
async def runtime_info():

    return {
        "runtime_management": True,
        "startup_lifecycle": True,
        "shutdown_lifecycle": True,
        "runtime_status": True,
        "readiness_check": True,
        "environment_configuration": True,
        "graceful_shutdown_logging": True,
        "secret_logging": False,
        "production_runtime": True,
    }


# ============================================================
# Signal handling
# ============================================================

def handle_shutdown_signal(
    signum: int,
    frame: Any,
):

    global shutdown_requested

    with runtime_lock:
        shutdown_requested = True

    logger.warning(
        "Shutdown signal received | signal=%s",
        signum,
    )


signal.signal(
    signal.SIGINT,
    handle_shutdown_signal,
)


# ============================================================
# Startup summary
# ============================================================

logger.info(
    "Exercise 135 - AgentOS Production Runtime initialized"
)

logger.info(
    "Production runtime configuration validated"
)

logger.info(
    "Server ready | host=%s | port=%s",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)


# ============================================================
# Run AgentOS
# ============================================================

if __name__ == "__main__":

    agent_os.serve(
        app=app,
        host=AGENT_OS_HOST,
        port=AGENT_OS_PORT,
        reload=False,
        access_log=True,
    )