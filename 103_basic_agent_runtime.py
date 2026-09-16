import logging
import time
import uuid

from agno.agent import Agent
from agno.models.ollama import Ollama


# ---------------------------------------------------------
# Production-style logging
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("basic_agent_runtime")


# ---------------------------------------------------------
# Agent Runtime
# ---------------------------------------------------------

class AgentRuntime:
    """Simple runtime responsible for executing an AI agent request."""

    def __init__(self):
        self.execution_id = None
        self.status = "CREATED"
        self.start_time = None
        self.end_time = None

        logger.info("Creating AI agent.")

        self.agent = Agent(
            model=Ollama(id="llama3.2"),
            instructions=[
                "You are a helpful AI assistant.",
                "Give clear and concise answers.",
            ],
        )

        logger.info("AI agent created successfully.")
        logger.info("AI model configured: llama3.2")

    def start(self):
        """Start a new runtime execution."""

        self.execution_id = str(uuid.uuid4())
        self.status = "RUNNING"
        self.start_time = time.time()

        logger.info("==============================================")
        logger.info("Starting agent runtime.")
        logger.info("Execution ID: %s", self.execution_id)
        logger.info("Runtime status: %s", self.status)
        logger.info("==============================================")

    def execute(self, message: str) -> str:
        """Execute the AI agent."""

        if self.status != "RUNNING":
            raise RuntimeError(
                "Runtime must be RUNNING before execute() is called."
            )

        logger.info("Executing agent request.")
        logger.info("User message: %s", message)

        try:
            response = self.agent.run(message)

            logger.info("Agent execution completed successfully.")

            return response.content

        except Exception:
            self.status = "FAILED"
            logger.exception("Agent execution failed.")
            raise

    def complete(self):
        """Complete the runtime execution."""

        self.end_time = time.time()

        duration = self.end_time - self.start_time

        self.status = "COMPLETED"

        logger.info("==============================================")
        logger.info("Agent runtime completed.")
        logger.info("Execution ID: %s", self.execution_id)
        logger.info("Runtime status: %s", self.status)
        logger.info("Execution duration: %.2f seconds", duration)
        logger.info("==============================================")


# ---------------------------------------------------------
# Main application
# ---------------------------------------------------------

def main():
    logger.info("==============================================")
    logger.info("Exercise 103 - Basic Agent Runtime")
    logger.info("Agno + Ollama + Llama 3.2")
    logger.info("==============================================")

    runtime = AgentRuntime()

    message = input("\nYou: ").strip()

    if not message:
        logger.warning("Empty user message received.")
        print("Please enter a message.")
        return

    try:
        runtime.start()

        response = runtime.execute(message)

        print("\nAI:", response)

        runtime.complete()

    except Exception as error:
        logger.error("Runtime execution failed: %s", error)
        print("\nAI Runtime Error:", error)

    logger.info("Exercise 103 completed.")


# ---------------------------------------------------------
# Application entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()