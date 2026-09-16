import logging

from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================
# Logging Configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_chat_interface")


# ============================================================
# Create AI Agent
# ============================================================

def create_agent() -> Agent:
    """Create and configure the Agno chat agent."""

    logger.info("Starting chat agent creation.")

    agent = Agent(
        model=Ollama(id="llama3.2"),
        instructions=[
            "You are a helpful AI assistant.",
            "Have a natural and friendly conversation with the user.",
            "Answer questions clearly and concisely.",
        ],
    )

    logger.info("Chat agent created successfully.")
    logger.info("Model configured: llama3.2")

    return agent


# ============================================================
# Process Chat Message
# ============================================================

def process_message(agent: Agent, user_message: str) -> None:
    """Send a user message to the AI agent."""

    logger.info("Processing chat message.")

    try:
        logger.info("Sending chat message to Agno agent.")

        response = agent.run(user_message)

        logger.info("AI response generated successfully.")

        print(f"\nAI: {response.content}\n")

    except Exception:
        logger.exception("Error while processing chat message.")

        print(
            "\nAI: Sorry, I could not process your message.\n"
        )


# ============================================================
# Main Chat Interface
# ============================================================

def main() -> None:
    """Run the continuous chat interface."""

    logger.info("Starting Chat Interface.")

    agent = create_agent()

    print("\n======================================")
    print("        GramSwaram Chat Interface")
    print("======================================")
    print("Start chatting with the AI agent.")
    print("Type 'exit' to end the conversation.")
    print()

    logger.info("Chat interface initialized successfully.")

    message_count = 0

    while True:

        user_message = input("You: ").strip()

        # ----------------------------------------------------
        # Empty message validation
        # ----------------------------------------------------

        if not user_message:
            logger.warning("Empty chat message received.")

            print("Please enter a message.")
            continue

        # ----------------------------------------------------
        # Exit command
        # ----------------------------------------------------

        if user_message.lower() == "exit":
            logger.info(
                "Exit command received after %d messages.",
                message_count,
            )

            print("\nGoodbye! 👋\n")
            break

        # ----------------------------------------------------
        # Process message
        # ----------------------------------------------------

        message_count += 1

        logger.info(
            "Chat message received. Message number: %d",
            message_count,
        )

        process_message(agent, user_message)

    logger.info(
        "Chat session ended. Total messages: %d",
        message_count,
    )

    logger.info("Chat Interface stopped.")


# ============================================================
# Application Entry Point
# ============================================================

if __name__ == "__main__":
    logger.info("Application starting.")

    main()

    logger.info("Application finished.")