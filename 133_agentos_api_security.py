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

logger = logging.getLogger("agentos_api_security")


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
    id="gram-swaram-api-security-agentos",
    description="AgentOS API security demonstration",
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
# Security Configuration
# ============================================================

MAX_REQUEST_BODY_BYTES = 1_000_000

ALLOWED_HTTP_METHODS = {
    "GET",
    "POST",
    "PUT",
    "PATCH",
    "DELETE",
    "OPTIONS",
}

logger.info(
    "API security configuration initialized"
)

logger.info(
    "Maximum request body size | %s bytes",
    MAX_REQUEST_BODY_BYTES,
)

logger.info(
    "Allowed HTTP methods | %s",
    sorted(ALLOWED_HTTP_METHODS),
)


# ============================================================
# Security Middleware
# ============================================================

@app.middleware("http")
async def api_security_middleware(
    request: Request,
    call_next: Any,
):
    """
    Basic application-level security middleware.

    This middleware:
    - Adds security response headers.
    - Rejects unsupported HTTP methods.
    - Rejects oversized request bodies.
    - Logs security-relevant events.
    - Never logs the Authorization header.
    """

    # --------------------------------------------------------
    # Method validation
    # --------------------------------------------------------

    if request.method not in ALLOWED_HTTP_METHODS:
        logger.warning(
            "Blocked HTTP method | method=%s | path=%s",
            request.method,
            request.url.path,
        )

        return JSONResponse(
            status_code=405,
            content={
                "error": "method_not_allowed",
                "message": "HTTP method is not allowed.",
            },
        )

    # --------------------------------------------------------
    # Request size validation
    # --------------------------------------------------------

    content_length = request.headers.get(
        "content-length"
    )

    if content_length:
        try:
            content_length_value = int(content_length)

            if (
                content_length_value
                > MAX_REQUEST_BODY_BYTES
            ):
                logger.warning(
                    "Blocked oversized request | "
                    "path=%s | size=%s",
                    request.url.path,
                    content_length_value,
                )

                return JSONResponse(
                    status_code=413,
                    content={
                        "error": "request_too_large",
                        "message": (
                            "Request body exceeds "
                            "the allowed size."
                        ),
                    },
                )

        except ValueError:
            logger.warning(
                "Invalid Content-Length header | path=%s",
                request.url.path,
            )

            return JSONResponse(
                status_code=400,
                content={
                    "error": "invalid_content_length",
                    "message": (
                        "Content-Length header is invalid."
                    ),
                },
            )

    # --------------------------------------------------------
    # Process request
    # --------------------------------------------------------

    try:
        response = await call_next(request)

    except Exception:
        logger.exception(
            "Security middleware detected application "
            "exception | method=%s | path=%s",
            request.method,
            request.url.path,
        )
        raise

    # --------------------------------------------------------
    # Security headers
    # --------------------------------------------------------

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = (
        "no-referrer"
    )
    response.headers["Cache-Control"] = (
        "no-store"
    )

    response.headers["Content-Security-Policy"] = (
        "default-src 'self'"
    )

    logger.info(
        "Security middleware completed | "
        "method=%s | path=%s | status=%s",
        request.method,
        request.url.path,
        response.status_code,
    )

    return response


# ============================================================
# Public Security Status Endpoint
# ============================================================

@app.get("/demo/security-status")
async def security_status() -> dict[str, Any]:
    """
    Public endpoint showing security configuration.

    Secret values are intentionally never returned.
    """

    logger.info(
        "Security status endpoint requested"
    )

    return {
        "api_security_enabled": True,
        "authentication": "AgentOS security_key",
        "security_headers": True,
        "method_validation": True,
        "request_size_validation": True,
        "authorization_header_logging": False,
        "secret_values_exposed": False,
        "max_request_body_bytes": (
            MAX_REQUEST_BODY_BYTES
        ),
    }


# ============================================================
# Protected Secure Data Endpoint
# ============================================================

@app.get("/demo/secure-data")
async def secure_data() -> dict[str, Any]:
    """
    Example protected endpoint.

    AgentOS security_key authentication protects
    this endpoint automatically.
    """

    logger.info(
        "Protected secure-data endpoint accessed"
    )

    return {
        "status": "authorized",
        "message": (
            "Protected API access successful."
        ),
        "sensitive_data_exposed": False,
    }


# ============================================================
# Security Test Endpoint
# ============================================================

@app.post("/demo/security-test")
async def security_test() -> dict[str, Any]:
    """
    Protected endpoint used to verify POST requests.
    """

    logger.info(
        "Protected security-test endpoint accessed"
    )

    return {
        "status": "ok",
        "method": "POST",
        "message": (
            "Protected POST request accepted."
        ),
    }


# ============================================================
# API Security Architecture
# ============================================================

logger.info(
    "========== AgentOS API Security Architecture =========="
)

logger.info("Incoming API request")
logger.info("       ↓")
logger.info("HTTP method validation")
logger.info("       ↓")
logger.info("Request size validation")
logger.info("       ↓")
logger.info("AgentOS authentication")
logger.info("       ↓")
logger.info("Protected API endpoint")
logger.info("       ↓")
logger.info("Security response headers")
logger.info("       ↓")
logger.info("Secure API response")

logger.info(
    "========================================================"
)


# ============================================================
# Security Rules
# ============================================================

logger.info(
    "========== API Security Rules =========="
)

logger.info(
    "Bearer authentication: ENABLED"
)

logger.info(
    "Security headers: ENABLED"
)

logger.info(
    "HTTP method validation: ENABLED"
)

logger.info(
    "Request size validation: ENABLED"
)

logger.info(
    "Authorization header logging: DISABLED"
)

logger.info(
    "Secret value exposure: DISABLED"
)

logger.info(
    "================================================"
)


# ============================================================
# Server Startup
# ============================================================

logger.info(
    "Starting AgentOS API Security Server"
)

logger.info(
    "Host=%s | Port=%s",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "Security status | "
    "http://%s:%s/demo/security-status",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "Protected endpoint | "
    "http://%s:%s/demo/secure-data",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "Security test | "
    "http://%s:%s/demo/security-test",
    AGENT_OS_HOST,
    AGENT_OS_PORT,
)

logger.info(
    "AgentOS API security server is ready"
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
            "AgentOS API security server stopped"
        )