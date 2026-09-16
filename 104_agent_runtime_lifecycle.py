import logging
import time
import uuid
from enum import Enum

from agno.agent import Agent
from agno.models.ollama import Ollama


# ---------------------------------------------------------
# Production-style logging
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agent_runtime_lifecycle")


# ---------------------------------------------------------
# Runtime Lifecycle States
# ---------------------------------------------------------

class RuntimeStatus(Enum):
    CREATED = "CREATED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ---------------------------------------------------------
# Agent Runtime
# ---------------------------------------------------------

class AgentRuntime:
    """Agent runtime with an explicit execution lifecycle."""

    def __init__(self):
        self.execution_id = str(uuid.uuid4())
        self.status = RuntimeStatus.CREATED

        self.start_time = None
        self.end_time = None
        self.error = None

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
        logger.info(
            "Runtime created with execution ID: %s",
            self.execution_id,
        )
        logger.info("Initial runtime status: %s", self.status.value)

    def start(self):
        """Start the runtime lifecycle."""

        logger.info("----------------------------------------------")
        logger.info("Runtime lifecycle starting.")

        self.status = RuntimeStatus.STARTING

        logger.info("Runtime status: %s", self.status.value)

        self.start_time = time.time()

        self.status = RuntimeStatus.RUNNING

        logger.info("Runtime status: %s", self.status.value)
        logger.info("Agent runtime is now ready for execution.")
        logger.info("----------------------------------------------")

    def execute(self, message: str) -> str:
        """Execute an agent request."""

        if self.status != RuntimeStatus.RUNNING:
            raise RuntimeError(
                f"Cannot execute request while runtime status is "
                f"{self.status.value}."
            )

        logger.info("Agent execution started.")
        logger.info("Execution ID: %s", self.execution_id)
        logger.info("User message: %s", message)

        try:
            response = self.agent.run(message)

            logger.info("Agent execution completed successfully.")

            return response.content

        except Exception as error:
            self.fail(error)
            raise

    def complete(self):
        """Mark runtime execution as completed."""

        self.end_time = time.time()
        self.status = RuntimeStatus.COMPLETED

        duration = self.end_time - self.start_time

        logger.info("----------------------------------------------")
        logger.info("Runtime lifecycle completed.")
        logger.info("Execution ID: %s", self.execution_id)
        logger.info("Runtime status: %s", self.status.value)
        logger.info("Execution duration: %.2f seconds", duration)
        logger.info("----------------------------------------------")

    def fail(self, error: Exception):
        """Mark runtime execution as failed."""

        self.end_time = time.time()
        self.status = RuntimeStatus.FAILED
        self.error = str(error)

        duration = 0.0

        if self.start_time is not None:
            duration = self.end_time - self.start_time

        logger.error("----------------------------------------------")
        logger.error("Runtime lifecycle failed.")
        logger.error("Execution ID: %s", self.execution_id)
        logger.error("Runtime status: %s", self.status.value)
        logger.error("Execution duration: %.2f seconds", duration)
        logger.error("Error: %s", self.error)
        logger.error("----------------------------------------------")


# ---------------------------------------------------------
# Main Application
# ---------------------------------------------------------

def main():
    logger.info("==================================================")
    logger.info("Exercise 104 - Agent Runtime Lifecycle")
    logger.info("Agno + Ollama + Llama 3.2")
    logger.info("==================================================")

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

        print("\nRuntime Status:", runtime.status.value)
        print("Execution ID:", runtime.execution_id)

    except Exception as error:
        logger.error("Application execution failed: %s", error)

        print("\nAI Runtime Error:", error)
        print("Runtime Status:", runtime.status.value)

    logger.info("Exercise 104 completed.")


# ---------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()