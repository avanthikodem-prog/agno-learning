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

logger = logging.getLogger("agent_runtime_context")


# ---------------------------------------------------------
# Runtime Context
# ---------------------------------------------------------

@dataclass
class RuntimeContext:
    """Context available during one agent execution."""

    user_role: str
    language: str
    location: str
    request_type: str

    session_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    execution_id: str = field(
        default_factory=lambda: str(uuid.uuid4())
    )

    created_at: float = field(
        default_factory=time.time
    )


# ---------------------------------------------------------
# Agent Runtime
# ---------------------------------------------------------

class AgentRuntime:
    """Agent runtime that passes context to the AI agent."""

    def __init__(self, context: RuntimeContext):
        self.context = context
        self.status = "CREATED"
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

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

        logger.info("Runtime context created.")
        logger.info(
            "Session ID: %s",
            self.context.session_id,
        )
        logger.info(
            "Execution ID: %s",
            self.context.execution_id,
        )

    def start(self):
        """Start runtime execution."""

        self.status = "RUNNING"
        self.start_time = time.time()

        logger.info("----------------------------------------------")
        logger.info("Agent runtime started.")
        logger.info("Runtime status: %s", self.status)
        logger.info("----------------------------------------------")

    def build_context_message(self, user_message: str) -> str:
        """Build a message containing runtime context."""

        context_message = f"""
Runtime Context:
- User Role: {self.context.user_role}
- Language: {self.context.language}
- Location: {self.context.location}
- Request Type: {self.context.request_type}
- Session ID: {self.context.session_id}
- Execution ID: {self.context.execution_id}

User Request:
{user_message}
"""

        return context_message.strip()

    def execute(self, user_message: str) -> str:
        """Execute the agent using runtime context."""

        if self.status != "RUNNING":
            raise RuntimeError(
                "Runtime must be RUNNING before execution."
            )

        logger.info("Executing agent with runtime context.")
        logger.info(
            "User role: %s",
            self.context.user_role,
        )
        logger.info(
            "Language: %s",
            self.context.language,
        )
        logger.info(
            "Location: %s",
            self.context.location,
        )
        logger.info(
            "Request type: %s",
            self.context.request_type,
        )

        try:
            context_message = self.build_context_message(
                user_message
            )

            logger.info(
                "Runtime context attached to agent request."
            )

            response = self.agent.run(context_message)

            logger.info(
                "Agent response generated successfully."
            )

            return response.content

        except Exception:
            self.status = "FAILED"
            logger.exception(
                "Agent execution failed."
            )
            raise

    def complete(self):
        """Complete runtime execution."""

        self.end_time = time.time()
        self.status = "COMPLETED"

        duration = 0.0

        if self.start_time is not None:
            duration = self.end_time - self.start_time

        logger.info("----------------------------------------------")
        logger.info("Agent runtime completed.")
        logger.info(
            "Execution ID: %s",
            self.context.execution_id,
        )
        logger.info(
            "Runtime status: %s",
            self.status,
        )
        logger.info(
            "Execution duration: %.2f seconds",
            duration,
        )
        logger.info("----------------------------------------------")

    def display_context(self):
        """Display the runtime context."""

        print("\n" + "=" * 55)
        print("RUNTIME CONTEXT")
        print("=" * 55)

        print(
            f"User Role      : "
            f"{self.context.user_role}"
        )

        print(
            f"Language       : "
            f"{self.context.language}"
        )

        print(
            f"Location       : "
            f"{self.context.location}"
        )

        print(
            f"Request Type   : "
            f"{self.context.request_type}"
        )

        print(
            f"Session ID     : "
            f"{self.context.session_id}"
        )

        print(
            f"Execution ID   : "
            f"{self.context.execution_id}"
        )

        print("=" * 55)


# ---------------------------------------------------------
# Main Application
# ---------------------------------------------------------

def main():
    logger.info("==================================================")
    logger.info("Exercise 106 - Agent Runtime Context")
    logger.info("Agno + Ollama + Llama 3.2")
    logger.info("==================================================")

    # Example runtime context.
    context = RuntimeContext(
        user_role="customer",
        language="English",
        location="Hyderabad",
        request_type="information",
    )

    runtime = AgentRuntime(context)

    runtime.display_context()

    user_message = input("\nYou: ").strip()

    if not user_message:
        logger.warning(
            "Empty user message received."
        )
        print("Please enter a message.")
        return

    try:
        runtime.start()

        response = runtime.execute(user_message)

        print("\nAI:", response)

        runtime.complete()

    except Exception as error:
        logger.error(
            "Runtime execution failed: %s",
            error,
        )

        print(
            "\nAI Runtime Error:",
            error,
        )

    logger.info("Exercise 106 completed.")


# ---------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()