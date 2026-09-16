import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Optional

from agno.agent import Agent
from agno.models.ollama import Ollama


# ---------------------------------------------------------
# Production-style logging
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agent_runtime_state")


# ---------------------------------------------------------
# Runtime State
# ---------------------------------------------------------

@dataclass
class RuntimeState:
    """Stores the state of one agent runtime execution."""

    execution_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "CREATED"

    user_message: Optional[str] = None
    agent_response: Optional[str] = None

    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: Optional[float] = None

    execution_count: int = 0

    error: Optional[str] = None


# ---------------------------------------------------------
# Agent Runtime
# ---------------------------------------------------------

class AgentRuntime:
    """Agent runtime that maintains execution state."""

    def __init__(self):
        self.state = RuntimeState()

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
            "Runtime state created with execution ID: %s",
            self.state.execution_id,
        )

        logger.info(
            "Initial runtime state: %s",
            self.state.status,
        )

    def start(self):
        """Start the runtime and update its state."""

        self.state.status = "RUNNING"
        self.state.start_time = time.time()
        self.state.execution_count += 1

        logger.info("----------------------------------------------")
        logger.info("Runtime state updated.")
        logger.info("Execution ID: %s", self.state.execution_id)
        logger.info("Status: %s", self.state.status)
        logger.info(
            "Execution count: %s",
            self.state.execution_count,
        )
        logger.info("----------------------------------------------")

    def execute(self, message: str) -> str:
        """Execute the AI agent and update runtime state."""

        if self.state.status != "RUNNING":
            raise RuntimeError(
                "Runtime must be RUNNING before execution."
            )

        self.state.user_message = message

        logger.info("Agent execution started.")
        logger.info("User message stored in runtime state.")
        logger.info("User message: %s", message)

        try:
            response = self.agent.run(message)

            self.state.agent_response = response.content

            logger.info("Agent response stored in runtime state.")
            logger.info("Agent execution completed successfully.")

            return self.state.agent_response

        except Exception as error:
            self.state.status = "FAILED"
            self.state.error = str(error)
            self.state.end_time = time.time()

            if self.state.start_time is not None:
                self.state.duration = (
                    self.state.end_time - self.state.start_time
                )

            logger.exception("Agent execution failed.")

            raise

    def complete(self):
        """Complete the runtime and update final state."""

        self.state.end_time = time.time()

        if self.state.start_time is not None:
            self.state.duration = (
                self.state.end_time - self.state.start_time
            )

        self.state.status = "COMPLETED"

        logger.info("----------------------------------------------")
        logger.info("Runtime execution completed.")
        logger.info("Execution ID: %s", self.state.execution_id)
        logger.info("Status: %s", self.state.status)
        logger.info(
            "Execution duration: %.2f seconds",
            self.state.duration,
        )
        logger.info("----------------------------------------------")

    def display_state(self):
        """Display the complete runtime state."""

        print("\n" + "=" * 55)
        print("AGENT RUNTIME STATE")
        print("=" * 55)

        print(f"Execution ID    : {self.state.execution_id}")
        print(f"Status          : {self.state.status}")
        print(f"Execution Count : {self.state.execution_count}")
        print(f"User Message    : {self.state.user_message}")
        print(f"Start Time      : {self.state.start_time}")
        print(f"End Time        : {self.state.end_time}")

        if self.state.duration is not None:
            print(
                f"Duration        : "
                f"{self.state.duration:.2f} seconds"
            )
        else:
            print("Duration        : N/A")

        if self.state.agent_response:
            print(
                f"Response Stored : "
                f"{len(self.state.agent_response)} characters"
            )
        else:
            print("Response Stored : No")

        if self.state.error:
            print(f"Error           : {self.state.error}")
        else:
            print("Error           : None")

        print("=" * 55)


# ---------------------------------------------------------
# Main Application
# ---------------------------------------------------------

def main():
    logger.info("==================================================")
    logger.info("Exercise 105 - Agent Runtime State")
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

        runtime.display_state()

    except Exception as error:
        logger.error(
            "Runtime execution failed: %s",
            error,
        )

        print("\nAI Runtime Error:", error)

        runtime.display_state()

    logger.info("Exercise 105 completed.")


# ---------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()