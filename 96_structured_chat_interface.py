import logging
from datetime import datetime, timezone

from agno.agent import Agent
from agno.models.ollama import Ollama
from pydantic import BaseModel, Field, ValidationError


# ============================================================
# Logging Configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_structured_chat")


# ============================================================
# Structured Request Model
# ============================================================

class ChatRequest(BaseModel):
    """Represents a structured user chat request."""

    message_id: int = Field(gt=0)
    user_message: str = Field(min_length=1, max_length=1000)
    timestamp: str


# ============================================================
# Structured Response Model
# ============================================================

class ChatResponse(BaseModel):
    """Represents a structured AI chat response."""

    message_id: int
    user_message: str
    response: str
    status: str
    timestamp: str


# ============================================================
# Create AI Agent
# ============================================================

def create_agent() -> Agent:
    """Create and configure the Agno AI agent."""

    logger.info("Starting structured chat agent creation.")

    agent = Agent(
        model=Ollama(id="llama3.2"),
        instructions=[
            "You are a helpful AI assistant.",
            "Answer user questions clearly and concisely.",
        ],
    )

    logger.info("Structured chat agent created successfully.")
    logger.info("Model configured: llama3.2")

    return agent


# ============================================================
# Create Chat Request
# ============================================================

def create_chat_request(
    message_id: int,
    user_message: str,
) -> ChatRequest:
    """Create and validate a structured chat request."""

    logger.info(
        "Creating structured request for message ID: %d",
        message_id,
    )

    request = ChatRequest(
        message_id=message_id,
        user_message=user_message,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    logger.info(
        "Structured request validated successfully. Message ID: %d",
        message_id,
    )

    return request


# ============================================================
# Process Chat Request
# ============================================================

def process_chat_request(
    agent: Agent,
    request: ChatRequest,
) -> ChatResponse:
    """Process a structured request and return a structured response."""

    logger.info(
        "Processing structured request. Message ID: %d",
        request.message_id,
    )

    try:
        logger.info(
            "Sending message ID %d to Agno agent.",
            request.message_id,
        )

        response = agent.run(request.user_message)

        logger.info(
            "AI response generated successfully for message ID: %d",
            request.message_id,
        )

        chat_response = ChatResponse(
            message_id=request.message_id,
            user_message=request.user_message,
            response=response.content,
            status="success",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        logger.info(
            "Structured response created successfully. Message ID: %d",
            request.message_id,
        )

        return chat_response

    except Exception:
        logger.exception(
            "Failed to process message ID: %d",
            request.message_id,
        )

        return ChatResponse(
            message_id=request.message_id,
            user_message=request.user_message,
            response="Sorry, something went wrong while processing your request.",
            status="error",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


# ============================================================
# Display Structured Response
# ============================================================

def display_response(chat_response: ChatResponse) -> None:
    """Display the structured AI response."""

    logger.info(
        "Displaying response for message ID: %d",
        chat_response.message_id,
    )

    print("\n--------------------------------------")
    print("STRUCTURED CHAT RESPONSE")
    print("--------------------------------------")
    print(f"Message ID : {chat_response.message_id}")
    print(f"User       : {chat_response.user_message}")
    print(f"Status     : {chat_response.status}")
    print(f"Timestamp  : {chat_response.timestamp}")
    print(f"AI         : {chat_response.response}")
    print("--------------------------------------\n")


# ============================================================
# Main Interface
# ============================================================

def main() -> None:
    """Run the structured chat interface."""

    logger.info("Starting Structured Chat Interface.")

    agent = create_agent()

    print("\n======================================")
    print("   GramSwaram Structured Chat")
    print("======================================")
    print("Type 'exit' to stop the application.")
    print()

    logger.info("Structured chat interface initialized.")

    message_id = 0

    while True:

        user_message = input("You: ").strip()

        # ----------------------------------------------------
        # Empty input validation
        # ----------------------------------------------------

        if not user_message:
            logger.warning("Empty user message received.")

            print("Please enter a message.")
            continue

        # ----------------------------------------------------
        # Exit command
        # ----------------------------------------------------

        if user_message.lower() == "exit":
            logger.info(
                "Exit command received after %d messages.",
                message_id,
            )

            print("\nGoodbye! 👋\n")
            break

        # ----------------------------------------------------
        # Generate message ID
        # ----------------------------------------------------

        message_id += 1

        logger.info(
            "Received user message. Message ID: %d",
            message_id,
        )

        # ----------------------------------------------------
        # Create structured request
        # ----------------------------------------------------

        try:

            chat_request = create_chat_request(
                message_id=message_id,
                user_message=user_message,
            )

        except ValidationError as error:

            logger.error(
                "Request validation failed: %s",
                error,
            )

            print("\nInvalid request. Please try again.\n")
            continue

        # ----------------------------------------------------
        # Process request
        # ----------------------------------------------------

        chat_response = process_chat_request(
            agent=agent,
            request=chat_request,
        )

        # ----------------------------------------------------
        # Display response
        # ----------------------------------------------------

        display_response(chat_response)

    logger.info(
        "Structured Chat Interface stopped. Total messages: %d",
        message_id,
    )


# ============================================================
# Application Entry Point
# ============================================================

if __name__ == "__main__":

    logger.info("Application starting.")

    main()

    logger.info("Application finished.")