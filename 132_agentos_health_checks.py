import logging
import os
import time
from typing import Any

import psycopg
import requests
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

logger = logging.getLogger("agentos_health_checks")


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
    os.getenv("AGENT_OS_PORT", "7777")
)
OS_SECURITY_KEY = os.getenv("OS_SECURITY_KEY")


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
    id="gram-swaram-health-agentos",
    description="AgentOS production health check demonstration",
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

logger.info(
    "AgentOS FastAPI application created"
)


# ============================================================
# Health Check Helper Functions
# ============================================================

def check_postgresql() -> dict[str, Any]:
    """
    Check whether PostgreSQL is reachable.
    """

    start_time = time.perf_counter()

    try:
        with psycopg.connect(
            POSTGRES_DB_URL,
            connect_timeout=5,
        ) as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        if result == (1,):
            logger.info(
                "PostgreSQL health check passed | "
                "duration_ms=%.2f",
                duration_ms,
            )

            return {
                "status": "healthy",
                "response_time_ms": round(
                    duration_ms,
                    2,
                ),
            }

        logger.warning(
            "PostgreSQL health check returned unexpected result"
        )

        return {
            "status": "unhealthy",
            "response_time_ms": round(
                duration_ms,
                2,
            ),
        }

    except Exception as exc:
        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.exception(
            "PostgreSQL health check failed | "
            "duration_ms=%.2f | error=%s",
            duration_ms,
            str(exc),
        )

        return {
            "status": "unhealthy",
            "response_time_ms": round(
                duration_ms,
                2,
            ),
            "error": "PostgreSQL connection failed",
        }


def check_ollama() -> dict[str, Any]:
    """
    Check whether Ollama is reachable.
    """

    start_time = time.perf_counter()

    try:
        response = requests.get(
            f"{OLLAMA_HOST}/api/tags",
            timeout=5,
        )

        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        if response.status_code == 200:
            logger.info(
                "Ollama health check passed | "
                "duration_ms=%.2f",
                duration_ms,
            )

            return {
                "status": "healthy",
                "response_time_ms": round(
                    duration_ms,
                    2,
                ),
                "model": OLLAMA_MODEL,
            }

        logger.warning(
            "Ollama health check returned status=%s",
            response.status_code,
        )

        return {
            "status": "unhealthy",
            "response_time_ms": round(
                duration_ms,
                2,
            ),
            "model": OLLAMA_MODEL,
        }

    except Exception as exc:
        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        logger.exception(
            "Ollama health check failed | "
            "duration_ms=%.2f | error=%s",
            duration_ms,
            str(exc),
        )

        return {
            "status": "unhealthy",
            "response_time_ms": round(
                duration_ms,
                2,
            ),
            "model": OLLAMA_MODEL,
            "error": "Ollama connection failed",
        }


# ============================================================
# Comprehensive Health Check
# ============================================================

@app.get("/demo/health-checks")
async def health_checks() -> dict[str, Any]:
    """
    Check AgentOS, PostgreSQL and Ollama health.
    """

    logger.info(
        "Comprehensive health check requested"
    )

    overall_start = time.perf_counter()

    postgres_health = check_postgresql()
    ollama_health = check_ollama()

    agentos_health = {
        "status": "healthy",
        "service": "AgentOS",
    }

    dependencies_healthy = (
        postgres_health["status"] == "healthy"
        and ollama_health["status"] == "healthy"
    )

    overall_status = (
        "healthy"
        if dependencies_healthy
        else "degraded"
    )

    overall_duration_ms = (
        time.perf_counter() - overall_start
    ) * 1000

    logger.info(
        "Comprehensive health check completed | "
        "overall_status=%s | duration_ms=%.2f",
        overall_status,
        overall_duration_ms,
    )

    return {
        "overall_status": overall_status,
        "agentos": agentos_health,
        "postgresql": postgres_health,
        "ollama": ollama_health,
        "checked_at": time.strftime(
            "%Y-%m-%dT%H:%M:%SZ",
            time.gmtime(),
        ),
    }


# ============================================================
# Readiness Check
# ============================================================

@app.get("/demo/readiness")
async def readiness_check() -> dict[str, Any]:
    """
    Check whether the application is ready to serve requests.
    """

    logger.info(
        "Readiness check requested"
    )

    postgres_health = check_postgresql()
    ollama_health = check_ollama()

    ready = (
        postgres_health["status"] == "healthy"
        and ollama_health["status"] == "healthy"
    )

    logger.info(
        "Readiness check completed | ready=%s",
        ready,
    )

    return {
        "ready": ready,
        "postgresql": postgres_health["status"],
        "ollama": ollama_health["status"],
    }


# ============================================================
# Liveness Check
# ============================================================

@app.get("/demo/liveness")
async def liveness_check() -> dict[str, Any]:
    """
    Check whether the AgentOS process is alive.
    """

    logger.info(
        "Liveness check requested"
    )

    return {
        "alive": True,
        "service": "AgentOS",
    }


# ============================================================
# Health Check Architecture
# ============================================================

logger.info(
    "========== AgentOS Health Check Architecture =========="
)

logger.info("Health request")
logger.info("       ↓")
logger.info("AgentOS process check")
logger.info("       ↓")
logger.info("PostgreSQL connectivity check")
logger.info("       ↓")
logger.info("Ollama connectivity check")
logger.info("       ↓")
logger.info("Overall health calculation")
logger.info("       ↓")
logger.info("Health / Readiness response")

logger.info(
    "========================================================"
)


# ============================================================
# Production Health Rules
# ============================================================

logger.info(
    "========== Production Health Rules =========="
)

logger.info(
    "AgentOS liveness check: ENABLED"
)

logger.info(
    "PostgreSQL connectivity check: ENABLED"
)

logger.info(
    "Ollama connectivity check: ENABLED"
)

logger.info(
    "Readiness check: ENABLED"
)

logger.info(
    "Secret logging: DISABLED"
)

logger.info(
    "================================================"
)


# ============================================================
# Server Startup
# ============================================================

logger.info(
    "Starting AgentOS Health Check Server"
)

logger.info(
    "Host=%s | Port=%s",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "Health checks | "
    "http://%s:%s/demo/health-checks",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "Readiness | "
    "http://%s:%s/demo/readiness",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "Liveness | "
    "http://%s:%s/demo/liveness",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "AgentOS health check server is ready"
)


# ============================================================
# Run AgentOS
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
            "AgentOS health check server stopped"
        )