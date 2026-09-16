import logging

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

logger = logging.getLogger("gram_swaram_web_ui")


# ---------------------------------------------------------
# FastAPI application
# ---------------------------------------------------------

app = FastAPI(
    title="GramSwaram Web UI Agent",
    description="Web interface for an Agno AI agent using Ollama.",
    version="1.0.0",
)


# ---------------------------------------------------------
# Request model
# ---------------------------------------------------------

class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=1000,
        description="Message sent by the user",
    )


# ---------------------------------------------------------
# Response model
# ---------------------------------------------------------

class ChatResponse(BaseModel):
    response: str
    status: str


# ---------------------------------------------------------
# Create Agno Agent
# ---------------------------------------------------------

def create_agent() -> Agent:
    logger.info("Starting Web UI AI agent creation.")

    agent = Agent(
        model=Ollama(id="llama3.2"),
        instructions=[
            "You are a helpful AI assistant.",
            "Answer user questions clearly and concisely.",
        ],
    )

    logger.info("Web UI AI agent created successfully.")
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

    <title>GramSwaram AI Assistant</title>

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
            font-size: 28px;
        }

        .header p {
            margin: 8px 0 0;
            color: #d1d5db;
        }

        .chat-box {
            height: 500px;
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
            outline: none;
        }

        #sendButton {
            padding: 14px 24px;
            border: none;
            border-radius: 8px;
            background: #2563eb;
            color: white;
            font-size: 16px;
            cursor: pointer;
        }

        #sendButton:hover {
            background: #1d4ed8;
        }

        #sendButton:disabled {
            background: #9ca3af;
            cursor: not-allowed;
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
            <p>Agno + Ollama + Llama 3.2</p>
        </div>


        <div
            id="chatBox"
            class="chat-box"
        >

            <div class="message assistant">

                <div class="label">
                    AI
                </div>

                Hello! Ask me anything.

            </div>

        </div>


        <div
            id="status"
            class="status"
        >
            Ready
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
            >
                Send
            </button>

        </div>

    </div>


    <script>

        const messageInput =
            document.getElementById("messageInput");

        const sendButton =
            document.getElementById("sendButton");

        const chatBox =
            document.getElementById("chatBox");

        const statusElement =
            document.getElementById("status");


        function addMessage(sender, message, className) {

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


        async function sendMessage() {

            const message =
                messageInput.value.trim();


            if (!message) {

                statusElement.textContent =
                    "Please enter a message.";

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
                            message: message
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


        messageInput.addEventListener(
            "keydown",
            function(event) {

                if (event.key === "Enter") {

                    sendMessage();

                }

            }
        );

    </script>

</body>

</html>
"""


# ---------------------------------------------------------
# Web UI endpoint
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
# Health endpoint
# ---------------------------------------------------------

@app.get("/health")
def health_check():

    logger.info("Health check requested.")

    return {
        "status": "healthy",
        "service": "GramSwaram Web UI Agent",
    }


# ---------------------------------------------------------
# Chat endpoint
# ---------------------------------------------------------

@app.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(request: ChatRequest) -> ChatResponse:

    logger.info("Web UI chat request received.")

    try:

        logger.info(
            "User message received: %s",
            request.message,
        )

        logger.info(
            "Sending message to Agno agent."
        )

        response = agent.run(
            request.message
        )

        logger.info(
            "AI response generated successfully."
        )

        return ChatResponse(
            response=response.content,
            status="success",
        )

    except Exception as error:

        logger.exception(
            "Failed to process Web UI request: %s",
            error,
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to process AI request.",
        )


# ---------------------------------------------------------
# Run application
# ---------------------------------------------------------

if __name__ == "__main__":

    import uvicorn

    logger.info(
        "Starting GramSwaram Web UI Agent."
    )

    uvicorn.run(
        "99_web_ui_agent_interface:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )