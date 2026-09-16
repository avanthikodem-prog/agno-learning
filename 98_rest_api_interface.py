import logging

from fastapi import APIRouter, FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from agno.agent import Agent
from agno.models.ollama import Ollama


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_rest_api")


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="GramSwaram REST API",
    description="REST API interface for an Agno AI agent using Ollama.",
    version="1.0.0",
)


# ---------------------------------------------------------
# Pydantic Request Model
# ---------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=1000,
        description="Message to send to the AI agent",
    )


# ---------------------------------------------------------
# Pydantic Response Model
# ---------------------------------------------------------

class ChatResponse(BaseModel):
    response: str
    status: str


# ---------------------------------------------------------
# Health Response Model
# ---------------------------------------------------------

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


# ---------------------------------------------------------
# Create Agno Agent
# ---------------------------------------------------------

def create_agent() -> Agent:
    logger.info("Starting REST API AI agent creation.")

    agent = Agent(
        model=Ollama(id="llama3.2"),
        instructions=[
            "You are a helpful AI assistant.",
            "Answer user questions clearly and concisely.",
        ],
    )

    logger.info("REST API AI agent created successfully.")
    logger.info("AI model configured: llama3.2")

    return agent


agent = create_agent()


# ---------------------------------------------------------
# API Router
# ---------------------------------------------------------

api_router = APIRouter(
    prefix="/api/v1",
)


# ---------------------------------------------------------
# Health Endpoint
# ---------------------------------------------------------

@api_router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
)
def health_check() -> HealthResponse:
    logger.info("REST API health check received.")

    return HealthResponse(
        status="healthy",
        service="GramSwaram REST API",
        version="v1",
    )


# ---------------------------------------------------------
# Chat Endpoint
# ---------------------------------------------------------

@api_router.post(
    "/chat",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
)
def chat(request: ChatRequest) -> ChatResponse:
    logger.info("REST API chat request received.")
    logger.info("User message: %s", request.message)

    try:
        logger.info("Sending request to Agno agent.")

        response = agent.run(request.message)

        logger.info("AI response generated successfully.")

        return ChatResponse(
            response=response.content,
            status="success",
        )

    except Exception as error:
        logger.exception(
            "Failed to process REST API chat request: %s",
            error,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process the AI request.",
        )


# ---------------------------------------------------------
# Register Router
# ---------------------------------------------------------

app.include_router(api_router)


# ---------------------------------------------------------
# Root Endpoint
# ---------------------------------------------------------

@app.get("/")
def root():
    logger.info("Root endpoint accessed.")

    return {
        "message": "GramSwaram REST API is running.",
        "version": "v1",
        "docs": "/docs",
    }


# ---------------------------------------------------------
# Application Startup
# ---------------------------------------------------------

@app.on_event("startup")
def startup_event():
    logger.info("======================================")
    logger.info("GramSwaram REST API")
    logger.info("Application started successfully.")
    logger.info("API version: v1")
    logger.info("======================================")


# ---------------------------------------------------------
# Run application directly
# ---------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting GramSwaram REST API server.")

    uvicorn.run(
        "98_rest_api_interface:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )