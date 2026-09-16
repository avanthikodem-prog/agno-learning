import logging
import time
import uuid
from dataclasses import dataclass
from typing import List

from agno.agent import Agent
from agno.models.ollama import Ollama


# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agent_runtime_events")


# ---------------------------------------------------------
# Runtime Event
# ---------------------------------------------------------

@dataclass
class RuntimeEvent:
    event_id: str
    event_type: str
    execution_id: str
    timestamp: float
    message: str


# ---------------------------------------------------------
# Agent Runtime
# ---------------------------------------------------------

class AgentRuntime:

    def __init__(self):
        self.execution_id = str(uuid.uuid4())
        self.status = "CREATED"
        self.start_time = None
        self.end_time = None

        self.events: List[RuntimeEvent] = []

        self.agent = Agent(
            model=Ollama(id="llama3.2"),
            instructions=[
                "You are a helpful AI assistant.",
                "Give short and clear answers.",
            ],
        )

        logger.info(
            "Runtime created | execution_id=%s",
            self.execution_id,
        )

        self.record_event(
            "RUNTIME_CREATED",
            "Runtime object created",
        )

    # -----------------------------------------------------
    # Record Event
    # -----------------------------------------------------

    def record_event(self, event_type: str, message: str):

        event = RuntimeEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            execution_id=self.execution_id,
            timestamp=time.time(),
            message=message,
        )

        self.events.append(event)

        logger.info(
            "EVENT | type=%s | message=%s",
            event_type,
            message,
        )

    # -----------------------------------------------------
    # Start Runtime
    # -----------------------------------------------------

    def start(self):

        self.status = "RUNNING"
        self.start_time = time.time()

        self.record_event(
            "RUNTIME_STARTED",
            "Runtime execution started",
        )

    # -----------------------------------------------------
    # Agent Execution
    # -----------------------------------------------------

    def execute(self, user_message: str) -> str:

        self.record_event(
            "AGENT_STARTED",
            "Agent execution started",
        )

        logger.info(
            "Executing agent | message=%s",
            user_message,
        )

        try:

            response = self.agent.run(user_message)

            self.record_event(
                "AGENT_COMPLETED",
                "Agent execution completed",
            )

            return response.content

        except Exception as exc:

            self.record_event(
                "AGENT_FAILED",
                f"Agent execution failed: {exc}",
            )

            self.status = "FAILED"

            logger.exception(
                "Agent execution failed",
            )

            raise

    # -----------------------------------------------------
    # Complete Runtime
    # -----------------------------------------------------

    def complete(self):

        self.status = "COMPLETED"
        self.end_time = time.time()

        duration = self.end_time - self.start_time

        self.record_event(
            "RUNTIME_COMPLETED",
            f"Runtime completed in {duration:.2f} seconds",
        )

    # -----------------------------------------------------
    # Display Events
    # -----------------------------------------------------

    def display_events(self):

        print("\n" + "=" * 75)
        print("RUNTIME EVENT HISTORY")
        print("=" * 75)

        for event in self.events:

            event_time = time.strftime(
                "%H:%M:%S",
                time.localtime(event.timestamp),
            )

            print(
                f"{event_time} | "
                f"{event.event_type:<20} | "
                f"{event.message}"
            )

        print("=" * 75)

    # -----------------------------------------------------
    # Display Runtime Summary
    # -----------------------------------------------------

    def display_summary(self):

        duration = None

        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time

        print("\n" + "=" * 60)
        print("AGENT RUNTIME SUMMARY")
        print("=" * 60)

        print(f"Execution ID : {self.execution_id}")
        print(f"Status       : {self.status}")
        print(f"Events       : {len(self.events)}")

        if duration is not None:
            print(f"Duration     : {duration:.2f} seconds")

        print("=" * 60)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    logger.info("Starting Exercise 108")

    runtime = AgentRuntime()

    runtime.start()

    user_message = "What is an AI agent?"

    response = runtime.execute(user_message)

    runtime.complete()

    print("\nAI RESPONSE:")
    print(response)

    runtime.display_events()

    runtime.display_summary()

    logger.info(
        "Exercise 108 completed successfully"
    )


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()