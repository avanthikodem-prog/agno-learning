import logging
import uuid
from typing import Dict, List

import uvicorn
from agno.agent import Agent
from agno.models.ollama import Ollama
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field


# ============================================================
# Logging Configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("end_to_end_ai_agent_interface")


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="GramSwaram End-to-End AI Agent Interface",
    description="Complete AI agent interface using FastAPI, Agno and Ollama.",
    version="1.0.0",
)


# ============================================================
# Session Storage
# ============================================================

sessions: Dict[str, List[dict]] = {}


# ============================================================
# Pydantic Models
# ============================================================

class ChatRequest(BaseModel):
    session_id: str = Field(..., min_length=1)
    message: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    session_id: str
    response: str
    status: str


class CreateSessionResponse(BaseModel):
    session_id: str
    status: str


class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]
    message_count: int


class HealthResponse(BaseModel):
    status: str
    service: str
    model: str
    active_sessions: int


# ============================================================
# AI Agent Creation
# ============================================================

def create_agent() -> Agent:
    """Create and configure the Agno AI agent."""

    logger.info("Starting AI agent creation.")

    try:
        agent = Agent(
            model=Ollama(id="llama3.2"),
            instructions=[
                "You are GramSwaram AI Assistant.",
                "You are a helpful and friendly AI assistant.",
                "Give clear and simple explanations.",
                "Keep answers relevant to the user's question.",
                "When explaining technical concepts, use simple examples.",
            ],
        )

        logger.info("Agno AI agent created successfully.")
        logger.info("AI model configured: llama3.2")

        return agent

    except Exception:
        logger.exception("Failed to create AI agent.")
        raise


# ============================================================
# Web UI
# ============================================================

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>GramSwaram AI Assistant</title>

    <style>

        * {
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            margin: 0;
            padding: 30px;
        }

        .container {
            max-width: 900px;
            margin: auto;
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        }

        h1 {
            margin-bottom: 5px;
        }

        .subtitle {
            color: #666;
            margin-bottom: 20px;
        }

        .session-box {
            background: #f0f2f5;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            word-break: break-all;
        }

        #chat {
            min-height: 350px;
            max-height: 500px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
            background: #fafafa;
        }

        .message {
            margin-bottom: 15px;
            padding: 12px;
            border-radius: 8px;
            line-height: 1.5;
            white-space: pre-wrap;
        }

        .user {
            background: #e8f0fe;
        }

        .ai {
            background: #e8f5e9;
        }

        .system {
            background: #fff3cd;
        }

        .error {
            background: #ffebee;
            color: #b71c1c;
        }

        textarea {
            width: 100%;
            min-height: 90px;
            padding: 12px;
            border: 1px solid #ccc;
            border-radius: 8px;
            resize: vertical;
            font-family: Arial, sans-serif;
            font-size: 15px;
        }

        button {
            padding: 10px 16px;
            margin: 8px 5px 0 0;
            border: none;
            border-radius: 6px;
            cursor: pointer;
            font-size: 14px;
        }

        .send {
            background: #1976d2;
            color: white;
        }

        .history {
            background: #757575;
            color: white;
        }

        .clear {
            background: #d32f2f;
            color: white;
        }

        .health {
            background: #388e3c;
            color: white;
        }

        button:hover {
            opacity: 0.85;
        }

        .status {
            margin-top: 15px;
            color: #555;
            font-size: 14px;
        }

        .message-count {
            margin-top: 10px;
            font-size: 14px;
            color: #666;
        }

    </style>

</head>


<body>

<div class="container">

    <h1>GramSwaram AI Assistant</h1>

    <div class="subtitle">
        FastAPI + Agno + Ollama + Llama 3.2
    </div>

    <div class="session-box">

        Session ID:

        <strong id="sessionId">
            Creating...
        </strong>

    </div>

    <div id="chat"></div>

    <textarea
        id="message"
        placeholder="Type your message here..."
    ></textarea>

    <br>

    <button
        class="send"
        onclick="sendMessage()"
    >
        Send
    </button>

    <button
        class="history"
        onclick="showHistory()"
    >
        Show History
    </button>

    <button
        class="clear"
        onclick="clearSession()"
    >
        Clear Session
    </button>

    <button
        class="health"
        onclick="checkHealth()"
    >
        Health
    </button>

    <div
        class="status"
        id="status"
    >
        Starting application...
    </div>

    <div
        class="message-count"
        id="messageCount"
    >
        Messages: 0
    </div>

</div>


<script>


// ============================================================
// Global Session Variable
// ============================================================

let sessionId = null;


// ============================================================
// Add Message To Chat
// ============================================================

function addMessage(sender, text, type) {

    const chat = document.getElementById("chat");

    const div = document.createElement("div");

    div.className = "message " + type;

    const senderElement = document.createElement("strong");

    senderElement.innerText = sender;

    const contentElement = document.createElement("div");

    contentElement.innerText = text;

    div.appendChild(senderElement);

    div.appendChild(
        document.createElement("br")
    );

    div.appendChild(contentElement);

    chat.appendChild(div);

    chat.scrollTop = chat.scrollHeight;
}


// ============================================================
// Set Status
// ============================================================

function setStatus(text) {

    document.getElementById("status").innerText = text;
}


// ============================================================
// Update Message Count
// ============================================================

function updateMessageCount(count) {

    document.getElementById("messageCount").innerText =
        "Messages: " + count;
}


// ============================================================
// Create Session
// ============================================================

async function createSession() {

    try {

        setStatus("Creating session...");

        const response = await fetch("/sessions", {
            method: "POST"
        });

        const data = await response.json();

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to create session."
            );
        }

        sessionId = data.session_id;

        document.getElementById("sessionId").innerText =
            sessionId;

        updateMessageCount(0);

        setStatus("Session ready");

        addMessage(
            "AI",
            "Hello! Your conversation session has started.",
            "ai"
        );

        console.log(
            "[GramSwaram] Session created:",
            sessionId
        );

    } catch (error) {

        console.error(error);

        setStatus("Session creation failed.");

        addMessage(
            "Error",
            error.message,
            "error"
        );
    }
}


// ============================================================
// Send Message
// ============================================================

async function sendMessage() {

    const messageBox =
        document.getElementById("message");

    const message =
        messageBox.value.trim();


    if (!message) {

        addMessage(
            "Error",
            "Please enter a message before sending.",
            "error"
        );

        return;
    }


    if (!sessionId) {

        addMessage(
            "Error",
            "No active session. Please refresh the page.",
            "error"
        );

        return;
    }


    addMessage(
        "You",
        message,
        "user"
    );


    messageBox.value = "";


    setStatus(
        "AI is processing..."
    );


    try {

        const response = await fetch(
            "/chat",
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    session_id: sessionId,
                    message: message
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.error ||
                "AI request failed."
            );
        }


        addMessage(
            "AI",
            data.response,
            "ai"
        );


        setStatus("Ready");


        await refreshHistory();


    } catch (error) {

        console.error(error);


        addMessage(
            "Error",
            error.message,
            "error"
        );


        setStatus(
            "Error occurred"
        );
    }
}


// ============================================================
// Show History
// ============================================================

async function showHistory() {

    if (!sessionId) {

        addMessage(
            "Error",
            "No active session.",
            "error"
        );

        return;
    }


    try {

        const response = await fetch(
            "/sessions/" +
            sessionId +
            "/history"
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to load history."
            );
        }


        addMessage(
            "System",
            "History contains " +
            data.message_count +
            " messages.",
            "system"
        );


        updateMessageCount(
            data.message_count
        );


        console.log(
            "Session history:",
            data
        );


        setStatus(
            "History loaded"
        );


    } catch (error) {

        console.error(error);


        addMessage(
            "Error",
            error.message,
            "error"
        );
    }
}


// ============================================================
// Refresh History
// ============================================================

async function refreshHistory() {

    if (!sessionId) {
        return;
    }


    try {

        const response = await fetch(
            "/sessions/" +
            sessionId +
            "/history"
        );


        if (!response.ok) {
            return;
        }


        const data = await response.json();


        updateMessageCount(
            data.message_count
        );


    } catch (error) {

        console.error(
            "History refresh failed:",
            error
        );
    }
}


// ============================================================
// Clear Session
// ============================================================

async function clearSession() {

    if (!sessionId) {

        addMessage(
            "Error",
            "No active session.",
            "error"
        );

        return;
    }


    try {

        const response = await fetch(
            "/sessions/" +
            sessionId,
            {
                method: "DELETE"
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to clear session."
            );
        }


        document.getElementById(
            "chat"
        ).innerHTML = "";


        addMessage(
            "System",
            "Previous session cleared successfully.",
            "system"
        );


        setStatus(
            "Creating new session..."
        );


        await createSession();


    } catch (error) {

        console.error(error);


        addMessage(
            "Error",
            error.message,
            "error"
        );
    }
}


// ============================================================
// Health Check
// ============================================================

async function checkHealth() {

    try {

        const response = await fetch(
            "/health"
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Health check failed."
            );
        }


        addMessage(
            "System",
            "Service: " +
            data.service +
            "\\nModel: " +
            data.model +
            "\\nStatus: " +
            data.status +
            "\\nActive Sessions: " +
            data.active_sessions,
            "system"
        );


        setStatus(
            "System healthy"
        );


    } catch (error) {

        console.error(error);


        addMessage(
            "Error",
            error.message,
            "error"
        );


        setStatus(
            "Health check failed"
        );
    }
}


// ============================================================
// Start Application
// ============================================================

createSession();

</script>

</body>

</html>
"""


# ============================================================
# Home Endpoint
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse,
)
async def home():

    logger.info("Web UI requested.")

    return HTML_PAGE


# ============================================================
# Health Endpoint
# ============================================================

@app.get(
    "/health",
    response_model=HealthResponse,
)
async def health_check():

    logger.info("Health check requested.")

    return HealthResponse(
        status="healthy",
        service="GramSwaram AI Assistant",
        model="llama3.2",
        active_sessions=len(sessions),
    )


# ============================================================
# Create Session Endpoint
# ============================================================

@app.post(
    "/sessions",
    response_model=CreateSessionResponse,
)
async def create_session():

    logger.info(
        "Session creation request received."
    )

    try:

        session_id = str(uuid.uuid4())

        sessions[session_id] = []

        logger.info(
            "Session created successfully: %s",
            session_id,
        )

        return CreateSessionResponse(
            session_id=session_id,
            status="created",
        )

    except Exception as exc:

        logger.exception(
            "Session creation failed."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to create session.",
        ) from exc


# ============================================================
# Chat Endpoint
# ============================================================

@app.post(
    "/chat",
    response_model=ChatResponse,
)
async def chat(request: ChatRequest):

    logger.info(
        "Chat request received."
    )

    logger.info(
        "Session ID: %s",
        request.session_id,
    )


    # --------------------------------------------------------
    # Session Validation
    # --------------------------------------------------------

    if request.session_id not in sessions:

        logger.warning(
            "Invalid session ID: %s",
            request.session_id,
        )

        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )


    # --------------------------------------------------------
    # Message Validation
    # --------------------------------------------------------

    if not request.message.strip():

        logger.warning(
            "Empty message received."
        )

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )


    try:

        # ----------------------------------------------------
        # Create Agent
        # ----------------------------------------------------

        agent = create_agent()


        logger.info(
            "Sending request to Agno agent."
        )


        # ----------------------------------------------------
        # Run Agent
        # ----------------------------------------------------

        response = agent.run(
            request.message
        )


        response_text = str(
            response.content
        )


        logger.info(
            "AI response generated successfully."
        )


        # ----------------------------------------------------
        # Store User Message
        # ----------------------------------------------------

        sessions[
            request.session_id
        ].append(
            {
                "role": "user",
                "content": request.message,
            }
        )


        # ----------------------------------------------------
        # Store AI Response
        # ----------------------------------------------------

        sessions[
            request.session_id
        ].append(
            {
                "role": "assistant",
                "content": response_text,
            }
        )


        logger.info(
            "Conversation history updated."
        )


        return ChatResponse(
            session_id=request.session_id,
            response=response_text,
            status="success",
        )


    except Exception as exc:

        logger.exception(
            "AI generation failed."
        )


        raise HTTPException(
            status_code=500,
            detail=(
                "AI service failed to generate "
                "a response. Please try again."
            ),
        ) from exc


# ============================================================
# Session History Endpoint
# ============================================================

@app.get(
    "/sessions/{session_id}/history",
    response_model=SessionHistoryResponse,
)
async def get_session_history(
    session_id: str,
):

    logger.info(
        "History requested for session: %s",
        session_id,
    )


    if session_id not in sessions:

        logger.warning(
            "Invalid session ID for history: %s",
            session_id,
        )

        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )


    history = sessions[session_id]


    return SessionHistoryResponse(
        session_id=session_id,
        messages=history,
        message_count=len(history),
    )


# ============================================================
# Delete Session Endpoint
# ============================================================

@app.delete(
    "/sessions/{session_id}"
)
async def delete_session(
    session_id: str,
):

    logger.info(
        "Delete session request received: %s",
        session_id,
    )


    if session_id not in sessions:

        logger.warning(
            "Invalid session ID for deletion: %s",
            session_id,
        )

        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )


    del sessions[session_id]


    logger.info(
        "Session deleted successfully: %s",
        session_id,
    )


    return {
        "session_id": session_id,
        "status": "deleted",
    }


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":

    logger.info(
        "=================================================="
    )

    logger.info(
        "GramSwaram End-to-End AI Agent Interface"
    )

    logger.info(
        "FastAPI + Agno + Ollama + Llama 3.2"
    )

    logger.info(
        "Starting application..."
    )

    logger.info(
        "Open browser at: http://127.0.0.1:8000"
    )

    logger.info(
        "=================================================="
    )


    uvicorn.run(
        "102_end_to_end_ai_agent_interface:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )