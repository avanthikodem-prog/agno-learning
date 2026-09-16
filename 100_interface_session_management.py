import logging
import uuid
from typing import Dict, List

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
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

logger = logging.getLogger("gram_swaram_session_management")


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="GramSwaram Session Management",
    description="Web AI agent with session-based conversations.",
    version="1.0.0",
)


# ---------------------------------------------------------
# Session storage
# ---------------------------------------------------------
# For this learning exercise, sessions are stored in memory.
#
# Example:
#
# {
#     "session-id": [
#         {"role": "user", "message": "Hello"},
#         {"role": "assistant", "message": "Hello!"},
#     ]
# }
#
# This data will disappear when the application stops.

sessions: Dict[str, List[dict]] = {}


# ---------------------------------------------------------
# Request models
# ---------------------------------------------------------

class CreateSessionResponse(BaseModel):
    session_id: str
    status: str


class ChatRequest(BaseModel):
    session_id: str = Field(
        min_length=1,
        description="Unique session identifier",
    )

    message: str = Field(
        min_length=1,
        max_length=1000,
        description="Message sent by the user",
    )


# ---------------------------------------------------------
# Response model
# ---------------------------------------------------------

class ChatResponse(BaseModel):
    session_id: str
    response: str
    status: str


# ---------------------------------------------------------
# Session history response
# ---------------------------------------------------------

class SessionHistoryResponse(BaseModel):
    session_id: str
    messages: List[dict]
    message_count: int


# ---------------------------------------------------------
# Create Agno Agent
# ---------------------------------------------------------

def create_agent() -> Agent:
    logger.info("Starting session management AI agent creation.")

    agent = Agent(
        model=Ollama(id="llama3.2"),
        instructions=[
            "You are a helpful AI assistant.",
            "Answer user questions clearly and concisely.",
        ],
    )

    logger.info("Session management AI agent created successfully.")
    logger.info("AI model configured: llama3.2")

    return agent


agent = create_agent()


# ---------------------------------------------------------
# Web UI
# ---------------------------------------------------------

HTML_PAGE = """
<!DOCTYPE html>

<html lang="en">

<head>

    <meta charset="UTF-8">

    <meta
        name="viewport"
        content="width=device-width, initial-scale=1.0"
    >

    <title>GramSwaram Session Chat</title>


    <style>

        * {
            box-sizing: border-box;
        }


        body {
            margin: 0;
            font-family: Arial, sans-serif;
            background: #f4f6f8;
        }


        .container {
            width: 90%;
            max-width: 900px;
            margin: 40px auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            overflow: hidden;
        }


        .header {
            padding: 24px;
            background: #1f2937;
            color: white;
        }


        .header h1 {
            margin: 0;
        }


        .header p {
            margin: 8px 0 0;
            color: #d1d5db;
        }


        .session {
            padding: 15px 20px;
            background: #f9fafb;
            border-bottom: 1px solid #e5e7eb;
            font-size: 14px;
        }


        .session span {
            font-weight: bold;
        }


        .chat-box {
            height: 450px;
            overflow-y: auto;
            padding: 24px;
        }


        .message {
            margin-bottom: 18px;
            padding: 14px 16px;
            border-radius: 10px;
            line-height: 1.5;
            white-space: pre-wrap;
        }


        .user {
            background: #e0f2fe;
            margin-left: 20%;
        }


        .assistant {
            background: #f3f4f6;
            margin-right: 20%;
        }


        .label {
            font-weight: bold;
            margin-bottom: 6px;
        }


        .input-area {
            display: flex;
            gap: 10px;
            padding: 20px;
            border-top: 1px solid #e5e7eb;
        }


        #messageInput {
            flex: 1;
            padding: 14px;
            border: 1px solid #d1d5db;
            border-radius: 8px;
            font-size: 16px;
        }


        #sendButton {
            padding: 14px 24px;
            border: none;
            border-radius: 8px;
            background: #2563eb;
            color: white;
            cursor: pointer;
        }


        #sendButton:disabled {
            background: #9ca3af;
            cursor: not-allowed;
        }


        .buttons {
            display: flex;
            gap: 10px;
            padding: 0 20px 20px;
        }


        .secondary-button {
            padding: 10px 16px;
            border: none;
            border-radius: 8px;
            background: #6b7280;
            color: white;
            cursor: pointer;
        }


        .status {
            padding: 10px 20px;
            font-size: 14px;
            color: #6b7280;
        }

    </style>

</head>


<body>


<div class="container">


    <div class="header">

        <h1>GramSwaram AI Assistant</h1>

        <p>
            Agno + Ollama + Llama 3.2
        </p>

    </div>


    <div class="session">

        Session ID:

        <span id="sessionId">
            Creating...
        </span>

    </div>


    <div
        id="chatBox"
        class="chat-box"
    >

        <div class="message assistant">

            <div class="label">
                AI
            </div>

            Hello! Your conversation session has started.

        </div>

    </div>


    <div
        id="status"
        class="status"
    >
        Creating session...
    </div>


    <div class="input-area">

        <input
            id="messageInput"
            type="text"
            placeholder="Type your message..."
            maxlength="1000"
        >

        <button
            id="sendButton"
            onclick="sendMessage()"
            disabled
        >
            Send
        </button>

    </div>


    <div class="buttons">

        <button
            class="secondary-button"
            onclick="clearSession()"
        >
            Clear Session
        </button>

        <button
            class="secondary-button"
            onclick="showHistory()"
        >
            Show History
        </button>

    </div>


</div>


<script>

    let sessionId = null;


    const messageInput =
        document.getElementById("messageInput");


    const sendButton =
        document.getElementById("sendButton");


    const chatBox =
        document.getElementById("chatBox");


    const statusElement =
        document.getElementById("status");


    const sessionIdElement =
        document.getElementById("sessionId");


    // -----------------------------------------------------
    // Create session
    // -----------------------------------------------------

    async function createSession() {

        try {

            const response =
                await fetch("/sessions", {

                    method: "POST"

                });


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Failed to create session."
                );

            }


            sessionId =
                data.session_id;


            sessionIdElement.textContent =
                sessionId;


            statusElement.textContent =
                "Session ready";


            sendButton.disabled =
                false;


            messageInput.focus();


        } catch (error) {

            console.error(error);

            statusElement.textContent =
                "Failed to create session.";

        }

    }


    // -----------------------------------------------------
    // Add message to UI
    // -----------------------------------------------------

    function addMessage(
        sender,
        message,
        className
    ) {

        const messageDiv =
            document.createElement("div");


        messageDiv.className =
            "message " + className;


        const label =
            document.createElement("div");


        label.className =
            "label";


        label.textContent =
            sender;


        const content =
            document.createElement("div");


        content.textContent =
            message;


        messageDiv.appendChild(label);

        messageDiv.appendChild(content);


        chatBox.appendChild(messageDiv);


        chatBox.scrollTop =
            chatBox.scrollHeight;

    }


    // -----------------------------------------------------
    // Send message
    // -----------------------------------------------------

    async function sendMessage() {

        const message =
            messageInput.value.trim();


        if (!message) {

            statusElement.textContent =
                "Please enter a message.";

            return;

        }


        if (!sessionId) {

            statusElement.textContent =
                "Session is not ready.";

            return;

        }


        addMessage(
            "You",
            message,
            "user"
        );


        messageInput.value = "";

        sendButton.disabled = true;

        statusElement.textContent =
            "AI is thinking...";


        try {

            const response =
                await fetch("/chat", {

                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({

                        session_id:
                            sessionId,

                        message:
                            message

                    })

                });


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Request failed."
                );

            }


            addMessage(
                "AI",
                data.response,
                "assistant"
            );


            statusElement.textContent =
                "Ready";


        } catch (error) {

            console.error(error);


            addMessage(
                "AI",
                "Sorry, something went wrong.",
                "assistant"
            );


            statusElement.textContent =
                "Request failed.";

        } finally {

            sendButton.disabled =
                false;

            messageInput.focus();

        }

    }


    // -----------------------------------------------------
    // Clear session
    // -----------------------------------------------------

    async function clearSession() {

        if (!sessionId) {

            return;

        }


        try {

            const response =
                await fetch(
                    "/sessions/" + sessionId,
                    {
                        method: "DELETE"
                    }
                );


            if (!response.ok) {

                throw new Error(
                    "Failed to clear session."
                );

            }


            chatBox.innerHTML = "";


            addMessage(
                "AI",
                "Session cleared. A new session will be created.",
                "assistant"
            );


            statusElement.textContent =
                "Creating new session...";


            sendButton.disabled =
                true;


            await createSession();


        } catch (error) {

            console.error(error);

            statusElement.textContent =
                "Failed to clear session.";

        }

    }


    // -----------------------------------------------------
    // Show session history
    // -----------------------------------------------------

    async function showHistory() {

        if (!sessionId) {

            return;

        }


        try {

            const response =
                await fetch(
                    "/sessions/" +
                    sessionId +
                    "/history"
                );


            const data =
                await response.json();


            if (!response.ok) {

                throw new Error(
                    data.detail ||
                    "Failed to load history."
                );

            }


            console.log(
                "Session history:",
                data
            );


            statusElement.textContent =
                "History contains " +
                data.message_count +
                " messages.";

        } catch (error) {

            console.error(error);

            statusElement.textContent =
                "Failed to load history.";

        }

    }


    // -----------------------------------------------------
    // Enter key
    // -----------------------------------------------------

    messageInput.addEventListener(
        "keydown",
        function(event) {

            if (event.key === "Enter") {

                sendMessage();

            }

        }
    );


    // -----------------------------------------------------
    // Start application
    // -----------------------------------------------------

    createSession();

</script>


</body>

</html>
"""


# ---------------------------------------------------------
# Root Web UI endpoint
# ---------------------------------------------------------

@app.get(
    "/",
    response_class=HTMLResponse,
)
def home() -> HTMLResponse:

    logger.info("Web UI page requested.")

    return HTMLResponse(
        content=HTML_PAGE
    )


# ---------------------------------------------------------
# Create session
# ---------------------------------------------------------

@app.post(
    "/sessions",
    response_model=CreateSessionResponse,
)
def create_session() -> CreateSessionResponse:

    logger.info("Session creation request received.")

    session_id = str(uuid.uuid4())

    sessions[session_id] = []

    logger.info(
        "New session created successfully: %s",
        session_id,
    )

    return CreateSessionResponse(
        session_id=session_id,
        status="created",
    )


# ---------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------

@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest) -> ChatResponse:

    logger.info(
        "Chat request received for session: %s",
        request.session_id,
    )


    if request.session_id not in sessions:

        logger.warning(
            "Unknown session requested: %s",
            request.session_id,
        )

        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )


    try:

        logger.info(
            "User message received for session %s: %s",
            request.session_id,
            request.message,
        )


        logger.info(
            "Sending message to Agno agent."
        )


        response = agent.run(request.message)


        logger.info(
            "AI response generated successfully."
        )


        sessions[
            request.session_id
        ].append(
            {
                "role": "user",
                "message": request.message,
            }
        )


        sessions[
            request.session_id
        ].append(
            {
                "role": "assistant",
                "message": response.content,
            }
        )


        logger.info(
            "Conversation history updated for session: %s",
            request.session_id,
        )


        return ChatResponse(
            session_id=request.session_id,
            response=response.content,
            status="success",
        )


    except Exception as error:

        logger.exception(
            "Failed to process session chat request: %s",
            error,
        )


        raise HTTPException(
            status_code=500,
            detail="Failed to process AI request.",
        )


# ---------------------------------------------------------
# Get session history
# ---------------------------------------------------------

@app.get(
    "/sessions/{session_id}/history",
    response_model=SessionHistoryResponse,
)
def get_session_history(
    session_id: str,
) -> SessionHistoryResponse:

    logger.info(
        "Session history requested: %s",
        session_id,
    )


    if session_id not in sessions:

        logger.warning(
            "Session not found: %s",
            session_id,
        )

        raise HTTPException(
            status_code=404,
            detail="Session not found.",
        )


    history = sessions[session_id]


    logger.info(
        "Returning %d messages for session: %s",
        len(history),
        session_id,
    )


    return SessionHistoryResponse(
        session_id=session_id,
        messages=history,
        message_count=len(history),
    )


# ---------------------------------------------------------
# Delete session
# ---------------------------------------------------------

@app.delete(
    "/sessions/{session_id}",
)
def delete_session(
    session_id: str,
):

    logger.info(
        "Session deletion requested: %s",
        session_id,
    )


    if session_id not in sessions:

        logger.warning(
            "Cannot delete unknown session: %s",
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


# ---------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------

@app.get("/health")
def health_check():

    logger.info("Health check requested.")

    return {
        "status": "healthy",
        "service": "GramSwaram Session Management",
        "active_sessions": len(sessions),
    }


# ---------------------------------------------------------
# Run application
# ---------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    logger.info(
        "Starting GramSwaram Session Management application."
    )

    uvicorn.run(
        "100_interface_session_management:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )