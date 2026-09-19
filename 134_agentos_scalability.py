import asyncio
import logging
import os
import time
from dataclasses import dataclass, asdict
from threading import Lock
from typing import Dict, Any

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

logger = logging.getLogger("agentos_scalability")


# ============================================================
# Environment
# ============================================================

load_dotenv()

POSTGRES_DB_URL = os.getenv("POSTGRES_DB_URL")
OS_SECURITY_KEY = os.getenv("OS_SECURITY_KEY")
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2")

AGENT_OS_HOST = os.getenv("AGENT_OS_HOST", "127.0.0.1")
AGENT_OS_PORT = int(os.getenv("AGENT_OS_PORT", "7777"))

MAX_CONCURRENT_REQUESTS = 5


# ============================================================
# Configuration validation
# ============================================================

if not POSTGRES_DB_URL:
    raise RuntimeError("POSTGRES_DB_URL is not configured")

if not OS_SECURITY_KEY:
    raise RuntimeError("OS_SECURITY_KEY is not configured")


logger.info("Environment configuration loaded")
logger.info(
    "Scalability limit configured | max_concurrent_requests=%s",
    MAX_CONCURRENT_REQUESTS,
)


# ============================================================
# PostgreSQL
# ============================================================

db = PostgresDb(
    id="gramswaram-agentos-db",
    db_url=POSTGRES_DB_URL,
)

logger.info("PostgreSQL database configured")


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
    "Ollama model configured | model=%s | host=%s",
    OLLAMA_MODEL,
    OLLAMA_HOST,
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

logger.info("Agent created | id=%s", agri_assistant.id)


# ============================================================
# AgentOS
# ============================================================

agent_os = AgentOS(
    id="gram-swaram-scalability-agentos",
    description="AgentOS scalability and concurrency demonstration",
    db=db,
    agents=[agri_assistant],
)

app = agent_os.get_app()

logger.info(
    "AgentOS application created | id=%s",
    "gram-swaram-scalability-agentos",
)


# ============================================================
# Scalability metrics
# ============================================================

@dataclass
class ScalabilityMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    active_requests: int = 0
    peak_concurrent_requests: int = 0
    total_response_time_ms: float = 0.0


metrics = ScalabilityMetrics()

metrics_lock = Lock()


# ============================================================
# Concurrency control
# ============================================================

request_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)


# ============================================================
# Request middleware
# ============================================================

@app.middleware("http")
async def scalability_middleware(request: Request, call_next):
    start_time = time.perf_counter()

    with metrics_lock:
        metrics.total_requests += 1

        metrics.active_requests += 1

        if metrics.active_requests > metrics.peak_concurrent_requests:
            metrics.peak_concurrent_requests = metrics.active_requests

        current_active = metrics.active_requests

    logger.info(
        "Request started | method=%s | path=%s | active_requests=%s",
        request.method,
        request.url.path,
        current_active,
    )

    try:
        async with request_semaphore:

            response = await call_next(request)

            elapsed_ms = (
                time.perf_counter() - start_time
            ) * 1000

            with metrics_lock:
                if response.status_code < 400:
                    metrics.successful_requests += 1
                else:
                    metrics.failed_requests += 1

                metrics.total_response_time_ms += elapsed_ms

            logger.info(
                "Request completed | method=%s | path=%s | "
                "status=%s | duration_ms=%.2f",
                request.method,
                request.url.path,
                response.status_code,
                elapsed_ms,
            )

            return response

    except Exception as exc:

        elapsed_ms = (
            time.perf_counter() - start_time
        ) * 1000

        with metrics_lock:
            metrics.failed_requests += 1
            metrics.total_response_time_ms += elapsed_ms

        logger.exception(
            "Request failed | method=%s | path=%s | error=%s",
            request.method,
            request.url.path,
            str(exc),
        )

        return JSONResponse(
            status_code=500,
            content={
                "error": "internal_server_error",
                "message": "Unexpected server error.",
            },
        )

    finally:

        with metrics_lock:
            metrics.active_requests -= 1

            remaining_active = metrics.active_requests

        logger.info(
            "Request released | path=%s | active_requests=%s",
            request.url.path,
            remaining_active,
        )


# ============================================================
# Scalability status
# ============================================================

@app.get("/demo/scalability")
async def scalability_status() -> Dict[str, Any]:

    with metrics_lock:
        snapshot = asdict(metrics)

    total = snapshot["total_requests"]

    if total > 0:
        average_response_time = (
            snapshot["total_response_time_ms"] / total
        )
    else:
        average_response_time = 0.0

    return {
        "scalability_enabled": True,
        "max_concurrent_requests": MAX_CONCURRENT_REQUESTS,
        "total_requests": snapshot["total_requests"],
        "successful_requests": snapshot["successful_requests"],
        "failed_requests": snapshot["failed_requests"],
        "active_requests": snapshot["active_requests"],
        "peak_concurrent_requests": snapshot[
            "peak_concurrent_requests"
        ],
        "average_response_time_ms": round(
            average_response_time,
            2,
        ),
    }


# ============================================================
# Concurrency demonstration
# ============================================================

async def simulated_work(task_id: int) -> Dict[str, Any]:

    start_time = time.perf_counter()

    logger.info(
        "Simulation task started | task_id=%s",
        task_id,
    )

    await asyncio.sleep(0.2)

    duration_ms = (
        time.perf_counter() - start_time
    ) * 1000

    logger.info(
        "Simulation task completed | task_id=%s | duration_ms=%.2f",
        task_id,
        duration_ms,
    )

    return {
        "task_id": task_id,
        "status": "completed",
        "duration_ms": round(duration_ms, 2),
    }


@app.get("/demo/concurrency-test")
async def concurrency_test():

    number_of_tasks = 10

    logger.info(
        "Starting concurrency test | tasks=%s | limit=%s",
        number_of_tasks,
        MAX_CONCURRENT_REQUESTS,
    )

    start_time = time.perf_counter()

    semaphore = asyncio.Semaphore(
        MAX_CONCURRENT_REQUESTS
    )

    async def limited_task(task_id: int):

        async with semaphore:
            return await simulated_work(task_id)

    tasks = [
        limited_task(task_id)
        for task_id in range(1, number_of_tasks + 1)
    ]

    results = await asyncio.gather(*tasks)

    total_duration_ms = (
        time.perf_counter() - start_time
    ) * 1000

    logger.info(
        "Concurrency test completed | tasks=%s | duration_ms=%.2f",
        number_of_tasks,
        total_duration_ms,
    )

    return {
        "status": "completed",
        "total_tasks": number_of_tasks,
        "max_concurrent_tasks": MAX_CONCURRENT_REQUESTS,
        "completed_tasks": len(results),
        "total_duration_ms": round(
            total_duration_ms,
            2,
        ),
        "results": results,
    }


# ============================================================
# Scalability information
# ============================================================

@app.get("/demo/scalability-info")
async def scalability_info():

    return {
        "service": "AgentOS",
        "scalability_enabled": True,
        "concurrency_control": True,
        "max_concurrent_requests": MAX_CONCURRENT_REQUESTS,
        "request_metrics": True,
        "peak_concurrency_tracking": True,
        "load_simulation": True,
        "shared_database": "PostgreSQL",
        "llm_provider": "Ollama",
        "production_note": (
            "This exercise demonstrates single-process "
            "concurrency control. Production deployments "
            "normally use multiple workers, load balancing, "
            "external monitoring and shared infrastructure."
        ),
    }


# ============================================================
# Startup
# ============================================================

logger.info(
    "Exercise 134 - AgentOS Scalability initialized successfully"
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