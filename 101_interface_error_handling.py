import logging
import uuid
from typing import Dict, List

from agno.agent import Agent
from agno.models.ollama import Ollama
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
import uvicorn


# ============================================================
# Logging Configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("interface_error_handling")


# ============================================================
# FastAPI Application
# ============================================================

app = FastAPI(
    title="GramSwaram AI Assistant - Error Handling",
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


class ErrorResponse(BaseModel):
    error: str
    detail: str


# ============================================================
# Create AI Agent
# ============================================================

def create_agent() -> Agent:
    logger.info("Starting AI agent creation.")

    try:
        agent = Agent(
            model=Ollama(id="llama3.2"),
            instructions=[
                "You are a helpful AI assistant.",
                "Give clear and simple answers.",
                "Keep responses relevant to the user's question.",
            ],
        )

        logger.info("AI agent created successfully.")
        logger.info("AI model configured: llama3.2")

        return agent

    except Exception:
        logger.exception("Failed to create AI agent.")
        raise


# ============================================================
# Global Exception Handler
# ============================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.exception(
        "Unhandled exception occurred while processing request: %s",
        request.url.path,
    )

    return {
        "error": "Internal Server Error",
        "detail": "An unexpected error occurred. Please try again later.",
    }


# ============================================================
# Web UI
# ============================================================

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <title>GramSwaram AI Assistant</title>

    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f4f6f8;
            margin: 0;
            padding: 30px;
        }

        .container {
            max-width: 850px;
            margin: auto;
            background: white;
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }

        h1 {
            margin-bottom: 5px;
        }

        .subtitle {
            color: #666;
            margin-bottom: 20px;
        }

        .session {
            background: #f0f2f5;
            padding: 12px;
            border-radius: 8px;
            margin-bottom: 20px;
            word-break: break-all;
        }

        #chat {
            min-height: 300px;
            max-height: 500px;
            overflow-y: auto;
            border: 1px solid #ddd;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 15px;
        }

        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
        }

        .user {
            background: #e8f0fe;
        }

        .ai {
            background: #e8f5e9;
        }

        .error {
            background: #ffebee;
            color: #b71c1c;
        }

        textarea {
            width: 100%;
            min-height: 80px;
            padding: 10px;
            box-sizing: border-box;
            border: 1px solid #ccc;
            border-radius: 8px;
            resize: vertical;
        }

        button {
            padding: 10px 16px;
            margin: 8px 5px 0 0;
            border: none;
            border-radius: 6px;
            cursor: pointer;
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

        .status {
            margin-top: 15px;
            color: #555;
        }
    </style>
</head>

<body>

<div class="container">

    <h1>GramSwaram AI Assistant</h1>

    <div class="subtitle">
        Agno + Ollama + Llama 3.2
    </div>

    <div class="session">
        Session ID:
        <strong id="sessionId">Creating...</strong>
    </div>

    <div id="chat"></div>

    <textarea
        id="message"
        placeholder="Type your message here..."
    ></textarea>

    <br>

    <button class="send" onclick="sendMessage()">
        Send
    </button>

    <button class="history" onclick="showHistory()">
        Show History
    </button>

    <button class="clear" onclick="clearSession()">
        Clear Session
    </button>

    <div class="status" id="status">
        Starting...
    </div>

</div>


<script>

let sessionId = null;


// ============================================================
// Add Message To UI
// ============================================================

function addMessage(sender, text, type) {

    const chat = document.getElementById("chat");

    const div = document.createElement("div");

    div.className = "message " + type;

    div.innerHTML =
        "<strong>" + sender + "</strong><br>" +
        text;

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
// Create Session
// ============================================================

async function createSession() {

    try {

        const response = await fetch("/sessions", {
            method: "POST"
        });

        if (!response.ok) {
            throw new Error("Failed to create session.");
        }

        const data = await response.json();

        sessionId = data.session_id;

        document.getElementById("sessionId").innerText =
            sessionId;

        setStatus("Session ready");

        addMessage(
            "AI",
            "Hello! Your conversation session has started.",
            "ai"
        );

        console.log("Session created:", sessionId);

    } catch (error) {

        console.error(error);

        setStatus("Session creation failed.");

        addMessage(
            "Error",
            "Unable to create a session.",
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


    // Client-side validation
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

    setStatus("AI is processing...");


    try {

        const response = await fetch("/chat", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({

                session_id: sessionId,

                message: message

            })
        });


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.error ||
                "Request failed."
            );
        }


        addMessage(
            "AI",
            data.response,
            "ai"
        );

        setStatus("Ready");


    } catch (error) {

        console.error(error);

        addMessage(
            "Error",
            error.message,
            "error"
        );

        setStatus("Error occurred");
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
                data.error ||
                "Unable to load history."
            );
        }


        addMessage(
            "System",
            "History contains " +
            data.message_count +
            " messages.",
            "ai"
        );


        console.log(
            "Session history:",
            data
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
            "/sessions/" + sessionId,
            {
                method: "DELETE"
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                data.error ||
                "Unable to clear session."
            );
        }


        document.getElementById("chat").innerHTML = "";

        addMessage(
            "System",
            "Session cleared successfully.",
            "ai"
        );

        setStatus("Session cleared");


        // Create a new session
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
// Start Application
// ============================================================

createSession();

</script>

</body>
</html>
"""


# ============================================================
# Home Page
# ============================================================

@app.get("/", response_class=HTMLResponse)
async def home():
    logger.info("Web UI requested.")
    return HTML_PAGE


# ============================================================
# Health Check
# ============================================================

@app.get("/health")
async def health_check():

    logger.info("Health check received.")

    return {
        "status": "healthy",
        "service": "GramSwaram AI Assistant",
        "model": "llama3.2",
    }


# ============================================================
# Create Session
# ============================================================

@app.post("/sessions", response_model=CreateSessionResponse)
async def create_session():

    try:

        session_id = str(uuid.uuid4())

        sessions[session_id] = []

        logger.info(
            "New session created: %s",
            session_id,
        )

        return CreateSessionResponse(
            session_id=session_id,
            status="created",
        )

    except Exception:

        logger.exception(
            "Failed to create session."
        )

        raise HTTPException(
            status_code=500,
            detail="Unable to create session.",
        )


# ============================================================
# Chat Endpoint
# ============================================================

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):

    logger.info(
        "Chat request received for session: %s",
        request.session_id,
    )


    # --------------------------------------------------------
    # Validate Session
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
    # Validate Message
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

        # Create AI agent
        agent = create_agent()


        logger.info(
            "Sending message to Agno agent."
        )


        # ----------------------------------------------------
        # Call AI
        # ----------------------------------------------------

        response = agent.run(
            request.message
        )


        # Extract response text
        response_text = str(response.content)


        logger.info(
            "AI response generated successfully."
        )


        # ----------------------------------------------------
        # Store User Message
        # ----------------------------------------------------

        sessions[request.session_id].append({

            "role": "user",

            "content": request.message,

        })


        # ----------------------------------------------------
        # Store AI Response
        # ----------------------------------------------------

        sessions[request.session_id].append({

            "role": "assistant",

            "content": response_text,

        })


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
# Session History
# ============================================================

@app.get(
    "/sessions/{session_id}/history",
    response_model=SessionHistoryResponse,
)
async def get_session_history(session_id: str):

    logger.info(
        "History requested for session: %s",
        session_id,
    )


    if session_id not in sessions:

        logger.warning(
            "History requested for invalid session: %s",
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
# Delete Session
# ============================================================

@app.delete("/sessions/{session_id}")
async def delete_session(session_id: str):

    logger.info(
        "Delete session request received: %s",
        session_id,
    )


    if session_id not in sessions:

        logger.warning(
            "Delete requested for invalid session: %s",
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
        "Starting GramSwaram Interface Error Handling API."
    )

    logger.info(
        "Open browser at: http://127.0.0.1:8000"
    )

    uvicorn.run(
        "101_interface_error_handling:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )