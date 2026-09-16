import logging

from fastapi import FastAPI, HTTPException
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

logger = logging.getLogger("gram_swaram_fastapi_interface")


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="GramSwaram FastAPI Agent Interface",
    description="FastAPI interface for an Agno AI agent using Ollama.",
    version="1.0.0",
)


# ---------------------------------------------------------
# Request and Response Models
# ---------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=1000,
        description="Message to send to the AI agent",
    )


class ChatResponse(BaseModel):
    response: str
    status: str


# ---------------------------------------------------------
# Create Agno Agent
# ---------------------------------------------------------

def create_agent() -> Agent:
    logger.info("Starting AI agent creation.")

    agent = Agent(
        model=Ollama(id="llama3.2"),
        instructions=[
            "You are a helpful AI assistant.",
            "Answer user questions clearly and concisely.",
        ],
    )

    logger.info("Agno AI agent created successfully.")
    logger.info("AI model configured: llama3.2")

    return agent


agent = create_agent()


# ---------------------------------------------------------
# Health Check Endpoint
# ---------------------------------------------------------

@app.get("/health")
def health_check():
    logger.info("Health check request received.")

    return {
        "status": "healthy",
        "service": "GramSwaram FastAPI Agent Interface",
    }


# ---------------------------------------------------------
# Chat Endpoint
# ---------------------------------------------------------

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    logger.info("Received chat request.")

    try:
        logger.info("User message received: %s", request.message)

        logger.info("Sending message to Agno agent.")

        response = agent.run(request.message)

        logger.info("AI response generated successfully.")

        return ChatResponse(
            response=response.content,
            status="success",
        )

    except Exception as error:
        logger.exception("Failed to process chat request: %s", error)

        raise HTTPException(
            status_code=500,
            detail="Failed to process the AI request.",
        )


# ---------------------------------------------------------
# Application startup
# ---------------------------------------------------------

@app.on_event("startup")
def startup_event():
    logger.info("======================================")
    logger.info("GramSwaram FastAPI Agent Interface")
    logger.info("Application started successfully.")
    logger.info("======================================")


# ---------------------------------------------------------
# Run application directly
# ---------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    logger.info("Starting FastAPI server.")

    uvicorn.run(
        "97_fastapi_agent_interface:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )