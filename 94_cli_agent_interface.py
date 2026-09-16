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

logger = logging.getLogger("gram_swaram_cli_interface")


# ============================================================
# Create AI Agent
# ============================================================

def create_agent() -> Agent:
    """Create and configure the Agno AI agent."""

    logger.info("Creating CLI AI agent.")

    agent = Agent(
        model=Ollama(id="llama3.2"),
        instructions=[
            "You are a helpful AI assistant.",
            "Answer questions clearly and concisely.",
        ],
    )

    logger.info("CLI AI agent created successfully.")
    logger.info("Model configured: llama3.2")

    return agent


# ============================================================
# Display Help
# ============================================================

def show_help() -> None:
    """Display available CLI commands."""

    logger.info("Displaying CLI help.")

    print("\nAvailable commands:")
    print("  /help   - Show available commands")
    print("  /status - Show agent status")
    print("  /clear  - Clear the terminal")
    print("  /exit   - Exit the application")
    print()


# ============================================================
# Display Agent Status
# ============================================================

def show_status() -> None:
    """Display the current agent status."""

    logger.info("Displaying agent status.")

    print("\nAgent Status")
    print("-------------------------")
    print("Status : Running")
    print("Framework : Agno")
    print("Model : Ollama / llama3.2")
    print("Interface : CLI")
    print("-------------------------\n")


# ============================================================
# Clear Terminal
# ============================================================

def clear_terminal() -> None:
    """Clear the terminal screen."""

    logger.info("Clearing terminal screen.")

    print("\033[2J\033[H", end="")


# ============================================================
# Process AI Request
# ============================================================

def process_ai_request(agent: Agent, user_input: str) -> None:
    """Send user input to the AI agent."""

    logger.info("Processing AI request.")

    try:
        logger.info("Sending request to Agno agent.")

        response = agent.run(user_input)

        logger.info("AI response generated successfully.")

        print(f"\nAI: {response.content}\n")

    except Exception:
        logger.exception("Error while processing AI request.")

        print(
            "\nAI: Sorry, an error occurred "
            "while processing your request.\n"
        )


# ============================================================
# Main CLI Interface
# ============================================================

def main() -> None:
    """Run the CLI AI agent interface."""

    logger.info("Starting CLI Agent Interface.")

    agent = create_agent()

    print("\n======================================")
    print("       GramSwaram CLI AI Agent")
    print("======================================")
    print("Type /help to see available commands.")
    print()

    logger.info("CLI interface initialized successfully.")

    while True:

        user_input = input("You: ").strip()

        # ----------------------------------------------------
        # Empty input
        # ----------------------------------------------------

        if not user_input:
            logger.warning("Empty input received.")

            print("Please enter a question or command.")
            continue

        # ----------------------------------------------------
        # CLI Commands
        # ----------------------------------------------------

        if user_input.lower() == "/help":
            logger.info("Help command received.")
            show_help()
            continue

        if user_input.lower() == "/status":
            logger.info("Status command received.")
            show_status()
            continue

        if user_input.lower() == "/clear":
            logger.info("Clear command received.")
            clear_terminal()
            continue

        if user_input.lower() == "/exit":
            logger.info("Exit command received.")

            print("\nGoodbye! 👋\n")

            break

        # ----------------------------------------------------
        # Normal AI Question
        # ----------------------------------------------------

        logger.info("Normal user question received.")

        process_ai_request(agent, user_input)

    logger.info("CLI Agent Interface stopped.")


# ============================================================
# Application Entry Point
# ============================================================

if __name__ == "__main__":
    logger.info("Application starting.")

    main()

    logger.info("Application finished.")