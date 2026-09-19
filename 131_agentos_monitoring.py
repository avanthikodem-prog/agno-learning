import logging
import os
import time
from threading import Lock
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

logger = logging.getLogger("agentos_monitoring")


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
    id="gram-swaram-monitoring-agentos",
    description="AgentOS production monitoring demonstration",
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
# Monitoring Metrics
# ============================================================

metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "total_response_time_ms": 0.0,
}

metrics_lock = Lock()


# ============================================================
# Request Monitoring Middleware
# ============================================================

@app.middleware("http")
async def monitoring_middleware(
    request: Request,
    call_next: Any,
):
    start_time = time.perf_counter()

    try:
        response = await call_next(request)

        duration_ms = (
            time.perf_counter() - start_time
        ) * 1000

        with metrics_lock:
            metrics["total_requests"] += 1
            metrics["total_response_time_ms"] += duration_ms

            if response.status_code < 400:
                metrics["successful_requests"] += 1
            else:
                metrics["failed_requests"] += 1

        logger.info(
            "Monitoring request | method=%s | path=%s | "
            "status=%s | duration_ms=%.2f",
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

        with metrics_lock:
            metrics["total_requests"] += 1
            metrics["failed_requests"] += 1
            metrics["total_response_time_ms"] += duration_ms

        logger.exception(
            "Monitoring request failed | method=%s | "
            "path=%s | duration_ms=%.2f",
            request.method,
            request.url.path,
            duration_ms,
        )

        raise


# ============================================================
# Monitoring Endpoint
# ============================================================

@app.get("/demo/monitoring")
async def monitoring_status() -> dict[str, Any]:
    with metrics_lock:
        total_requests = metrics["total_requests"]
        successful_requests = metrics[
            "successful_requests"
        ]
        failed_requests = metrics[
            "failed_requests"
        ]
        total_response_time_ms = metrics[
            "total_response_time_ms"
        ]

    if total_requests > 0:
        average_response_time_ms = (
            total_response_time_ms
            / total_requests
        )
    else:
        average_response_time_ms = 0.0

    logger.info(
        "Monitoring status requested | "
        "total_requests=%s | successful=%s | failed=%s | "
        "average_response_time_ms=%.2f",
        total_requests,
        successful_requests,
        failed_requests,
        average_response_time_ms,
    )

    return {
        "monitoring_enabled": True,
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "average_response_time_ms": round(
            average_response_time_ms,
            2,
        ),
    }


# ============================================================
# Metrics Endpoint
# ============================================================

@app.get("/demo/metrics")
async def metrics_status() -> dict[str, Any]:
    with metrics_lock:
        total_requests = metrics["total_requests"]
        successful_requests = metrics[
            "successful_requests"
        ]
        failed_requests = metrics[
            "failed_requests"
        ]

    if total_requests > 0:
        success_rate = (
            successful_requests
            / total_requests
        ) * 100
    else:
        success_rate = 0.0

    if total_requests > 0:
        failure_rate = (
            failed_requests
            / total_requests
        ) * 100
    else:
        failure_rate = 0.0

    logger.info(
        "Metrics requested | "
        "success_rate=%.2f%% | failure_rate=%.2f%%",
        success_rate,
        failure_rate,
    )

    return {
        "total_requests": total_requests,
        "successful_requests": successful_requests,
        "failed_requests": failed_requests,
        "success_rate_percent": round(
            success_rate,
            2,
        ),
        "failure_rate_percent": round(
            failure_rate,
            2,
        ),
    }


# ============================================================
# Monitoring Architecture
# ============================================================

logger.info(
    "========== AgentOS Monitoring Architecture =========="
)

logger.info("Incoming HTTP request")
logger.info("       ↓")
logger.info("Monitoring middleware")
logger.info("       ↓")
logger.info("Request counter")
logger.info("       ↓")
logger.info("Response status tracking")
logger.info("       ↓")
logger.info("Response time measurement")
logger.info("       ↓")
logger.info("Success / failure metrics")
logger.info("       ↓")
logger.info("Monitoring API")
logger.info(
    "======================================================"
)


# ============================================================
# Production Monitoring Rules
# ============================================================

logger.info(
    "========== Production Monitoring Rules =========="
)

logger.info(
    "Request count monitoring: ENABLED"
)

logger.info(
    "Response time monitoring: ENABLED"
)

logger.info(
    "Success/failure monitoring: ENABLED"
)

logger.info(
    "Average response time calculation: ENABLED"
)

logger.info(
    "Secret monitoring/logging: DISABLED"
)

logger.info(
    "================================================"
)


# ============================================================
# Server Startup
# ============================================================

logger.info(
    "Starting AgentOS Monitoring Server"
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
    "Monitoring endpoint | "
    "http://%s:%s/demo/monitoring",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "Metrics endpoint | "
    "http://%s:%s/demo/metrics",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "AgentOS monitoring server is ready"
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
            "AgentOS monitoring server stopped"
        )