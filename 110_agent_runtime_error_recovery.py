import logging
import time
import uuid
from dataclasses import dataclass
from typing import Optional

from agno.agent import Agent
from agno.models.ollama import Ollama


# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agent_runtime_error_recovery")


# ---------------------------------------------------------
# Runtime State
# ---------------------------------------------------------

@dataclass
class RuntimeState:
    execution_id: str
    status: str = "CREATED"
    attempts: int = 0
    max_attempts: int = 2
    error: Optional[str] = None
    recovery_attempted: bool = False
    start_time: Optional[float] = None
    end_time: Optional[float] = None


# ---------------------------------------------------------
# Agent Runtime
# ---------------------------------------------------------

class AgentRuntime:

    def __init__(self):

        self.state = RuntimeState(
            execution_id=str(uuid.uuid4())
        )

        self.agent = Agent(
            model=Ollama(id="llama3.2"),
            instructions=[
                "You are a helpful AI assistant.",
                "Give clear and concise answers.",
            ],
        )

        logger.info(
            "Runtime created | execution_id=%s",
            self.state.execution_id,
        )

    # -----------------------------------------------------
    # Start Runtime
    # -----------------------------------------------------

    def start(self):

        self.state.status = "RUNNING"
        self.state.start_time = time.time()

        logger.info(
            "Runtime started | execution_id=%s",
            self.state.execution_id,
        )

    # -----------------------------------------------------
    # Simulate Controlled Failure
    # -----------------------------------------------------

    def simulate_failure(self):

        logger.warning(
            "Simulating controlled runtime failure"
        )

        raise RuntimeError(
            "Simulated runtime failure for recovery testing"
        )

    # -----------------------------------------------------
    # Execute Agent
    # -----------------------------------------------------

    def execute(self, user_message: str) -> str:

        while self.state.attempts < self.state.max_attempts:

            self.state.attempts += 1

            logger.info(
                "Execution attempt started | attempt=%s/%s",
                self.state.attempts,
                self.state.max_attempts,
            )

            try:

                # -------------------------------------------------
                # First attempt intentionally fails.
                # -------------------------------------------------

                if self.state.attempts == 1:

                    self.simulate_failure()

                # -------------------------------------------------
                # Recovery attempt executes the real agent.
                # -------------------------------------------------

                logger.info(
                    "Recovery attempt executing agent"
                )

                response = self.agent.run(
                    user_message
                )

                logger.info(
                    "Agent execution succeeded | attempt=%s",
                    self.state.attempts,
                )

                self.state.status = "COMPLETED"

                return response.content

            except Exception as exc:

                self.state.error = str(exc)

                logger.error(
                    "Runtime error detected | attempt=%s | error=%s",
                    self.state.attempts,
                    exc,
                )

                # ---------------------------------------------
                # Check whether recovery is possible
                # ---------------------------------------------

                if self.state.attempts < self.state.max_attempts:

                    self.recover()

                else:

                    self.state.status = "FAILED"

                    logger.error(
                        "Maximum attempts reached | runtime failed"
                    )

                    return (
                        "The runtime could not complete "
                        "the request after recovery attempts."
                    )

        return "Runtime execution ended."

    # -----------------------------------------------------
    # Recovery
    # -----------------------------------------------------

    def recover(self):

        self.state.recovery_attempted = True

        logger.info(
            "Runtime recovery started"
        )

        # Clear the previous error before retrying.
        self.state.error = None

        logger.info(
            "Previous runtime error cleared"
        )

        logger.info(
            "Retrying agent execution"
        )

    # -----------------------------------------------------
    # Complete Runtime
    # -----------------------------------------------------

    def complete(self):

        self.state.end_time = time.time()

        if self.state.status != "FAILED":
            self.state.status = "COMPLETED"

        duration = (
            self.state.end_time
            - self.state.start_time
        )

        logger.info(
            "Runtime completed | status=%s | "
            "attempts=%s | duration=%.2f seconds",
            self.state.status,
            self.state.attempts,
            duration,
        )

    # -----------------------------------------------------
    # Display Runtime State
    # -----------------------------------------------------

    def display_state(self):

        duration = None

        if self.state.start_time and self.state.end_time:

            duration = (
                self.state.end_time
                - self.state.start_time
            )

        print("\n" + "=" * 65)
        print("RUNTIME ERROR RECOVERY REPORT")
        print("=" * 65)

        print(
            f"Execution ID       : "
            f"{self.state.execution_id}"
        )

        print(
            f"Status             : "
            f"{self.state.status}"
        )

        print(
            f"Attempts           : "
            f"{self.state.attempts}"
        )

        print(
            f"Recovery Attempted : "
            f"{self.state.recovery_attempted}"
        )

        print(
            f"Last Error         : "
            f"{self.state.error}"
        )

        if duration is not None:

            print(
                f"Duration           : "
                f"{duration:.2f} seconds"
            )

        print("=" * 65)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    logger.info(
        "Starting Exercise 110"
    )

    runtime = AgentRuntime()

    runtime.start()

    user_message = (
        "Explain what an AI agent is "
        "in simple terms."
    )

    response = runtime.execute(
        user_message
    )

    runtime.complete()

    print("\nAI RESPONSE:")
    print(response)

    runtime.display_state()

    logger.info(
        "Exercise 110 completed successfully"
    )


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()