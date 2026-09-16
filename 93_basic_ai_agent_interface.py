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

logger = logging.getLogger("gram_swaram_basic_interface")


# ============================================================
# Create AI Agent
# ============================================================

def create_agent() -> Agent:
    """Create and configure the Agno AI agent."""

    logger.info("Starting AI agent creation.")

    agent = Agent(
        model=Ollama(id="llama3.2"),
        instructions=[
            "You are a helpful AI assistant.",
            "Answer the user's questions clearly and concisely.",
        ],
    )

    logger.info("AI agent created successfully.")
    logger.info("AI model configured: llama3.2")

    return agent


# ============================================================
# Process User Input
# ============================================================

def process_user_input(agent: Agent, user_input: str) -> None:
    """Send user input to the AI agent and display the response."""

    logger.info("Processing user request.")

    try:
        logger.info("Sending request to Agno agent.")

        response = agent.run(user_input)

        logger.info("AI agent successfully generated a response.")

        print(f"\nAI: {response.content}\n")

    except Exception:
        logger.exception("Failed to process user request.")
        print(
            "\nAI: Sorry, something went wrong "
            "while processing your request.\n"
        )


# ============================================================
# Main Interface
# ============================================================

def main() -> None:
    """Run the Basic AI Agent Interface."""

    logger.info("Starting Basic AI Agent Interface.")

    agent = create_agent()

    print("\n======================================")
    print("      GramSwaram AI Agent Interface")
    print("======================================")
    print("Type 'exit' to stop the application.\n")

    logger.info("User interface initialized successfully.")

    while True:

        user_input = input("You: ").strip()

        # ----------------------------------------------------
        # Empty input validation
        # ----------------------------------------------------

        if not user_input:
            logger.warning("Empty user input received.")
            print("Please enter a question.")
            continue

        # ----------------------------------------------------
        # Exit command
        # ----------------------------------------------------

        if user_input.lower() == "exit":
            logger.info("Exit command received from user.")
            print("Goodbye!")
            break

        logger.info("User input received.")

        # ----------------------------------------------------
        # Process request
        # ----------------------------------------------------

        process_user_input(agent, user_input)

    logger.info("Basic AI Agent Interface stopped.")


# ============================================================
# Application Entry Point
# ============================================================

if __name__ == "__main__":
    logger.info("Application starting.")
    main()
    logger.info("Application finished.")