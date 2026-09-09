import logging

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================
# 1. LOGGER CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gramsw aram_agent")

logger.info("Starting GramSwaram Agent API")


# ============================================================
# 2. FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="GramSwaram Agent API",
    description="Production-style API for a GramSwaram Agno Agent",
    version="1.0.0",
)


# ============================================================
# 3. AGNO AGENT
# ============================================================

agent = Agent(
    name="GramSwaram API Agent",
    model=Ollama(id="llama3.2"),
    instructions=[
        "You are a helpful GramSwaram assistant.",
        "Answer questions clearly.",
        "Do not invent information.",
        "If you do not know something, say that you do not know.",
    ],
)

logger.info("Agno agent initialized")


# ============================================================
# 4. REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str


# ============================================================
# 5. RESPONSE MODEL
# ============================================================

class ChatResponse(BaseModel):
    response: str


# ============================================================
# 6. HEALTH CHECK
# ============================================================

@app.get("/health")
def health_check():

    logger.info("Health check requested")

    return {
        "status": "healthy",
        "service": "GramSwaram Agent API",
    }


# ============================================================
# 7. CHAT ENDPOINT
# ============================================================

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    logger.info("Chat request received")

    logger.info(
        "User message length: %d characters",
        len(request.message),
    )

    try:

        logger.info("Sending request to Agno agent")

        result = agent.run(request.message)

        logger.info("Agent response generated successfully")

        return ChatResponse(
            response=result.content
        )

    except Exception:

        logger.exception("Agent execution failed")

        raise HTTPException(
            status_code=500,
            detail="Agent failed to process the request.",
        )