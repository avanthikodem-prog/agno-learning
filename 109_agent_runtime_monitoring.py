import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import List, Optional

from agno.agent import Agent
from agno.models.ollama import Ollama


# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agent_runtime_monitoring")


# ---------------------------------------------------------
# Runtime Event
# ---------------------------------------------------------

@dataclass
class RuntimeEvent:
    event_type: str
    timestamp: float
    message: str


# ---------------------------------------------------------
# Runtime Metrics
# ---------------------------------------------------------

@dataclass
class RuntimeMetrics:
    execution_id: str
    status: str = "CREATED"
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    duration: float = 0.0
    event_count: int = 0
    tool_calls: int = 0
    response_length: int = 0
    error: Optional[str] = None


# ---------------------------------------------------------
# Runtime Monitor
# ---------------------------------------------------------

class RuntimeMonitor:

    def __init__(self, metrics: RuntimeMetrics):
        self.metrics = metrics

        logger.info(
            "Runtime monitor initialized | execution_id=%s",
            metrics.execution_id,
        )

    # -----------------------------------------------------
    # Record Event
    # -----------------------------------------------------

    def record_event(self, event: RuntimeEvent):

        self.metrics.event_count += 1

        logger.info(
            "MONITOR EVENT | type=%s | message=%s",
            event.event_type,
            event.message,
        )

    # -----------------------------------------------------
    # Start Monitoring
    # -----------------------------------------------------

    def start(self):

        self.metrics.start_time = time.time()
        self.metrics.status = "RUNNING"

        logger.info(
            "Monitoring started | execution_id=%s",
            self.metrics.execution_id,
        )

    # -----------------------------------------------------
    # Complete Monitoring
    # -----------------------------------------------------

    def complete(self):

        self.metrics.end_time = time.time()

        if self.metrics.start_time:
            self.metrics.duration = (
                self.metrics.end_time
                - self.metrics.start_time
            )

        self.metrics.status = "COMPLETED"

        logger.info(
            "Monitoring completed | duration=%.2f seconds",
            self.metrics.duration,
        )

    # -----------------------------------------------------
    # Record Error
    # -----------------------------------------------------

    def record_error(self, error: str):

        self.metrics.status = "FAILED"
        self.metrics.error = error

        logger.error(
            "Runtime error recorded | error=%s",
            error,
        )

    # -----------------------------------------------------
    # Display Metrics
    # -----------------------------------------------------

    def display_metrics(self):

        print("\n" + "=" * 65)
        print("RUNTIME MONITORING REPORT")
        print("=" * 65)

        print(
            f"Execution ID    : "
            f"{self.metrics.execution_id}"
        )

        print(
            f"Status          : "
            f"{self.metrics.status}"
        )

        print(
            f"Duration        : "
            f"{self.metrics.duration:.2f} seconds"
        )

        print(
            f"Event Count     : "
            f"{self.metrics.event_count}"
        )

        print(
            f"Tool Calls      : "
            f"{self.metrics.tool_calls}"
        )

        print(
            f"Response Length : "
            f"{self.metrics.response_length} characters"
        )

        print(
            f"Error           : "
            f"{self.metrics.error}"
        )

        print("=" * 65)


# ---------------------------------------------------------
# Agent Runtime
# ---------------------------------------------------------

class AgentRuntime:

    def __init__(self):

        self.execution_id = str(uuid.uuid4())

        self.metrics = RuntimeMetrics(
            execution_id=self.execution_id
        )

        self.monitor = RuntimeMonitor(
            self.metrics
        )

        self.events: List[RuntimeEvent] = []

        self.agent = Agent(
            model=Ollama(id="llama3.2"),
            instructions=[
                "You are a helpful AI assistant.",
                "Give a clear and concise answer.",
            ],
        )

        logger.info(
            "Agent runtime created | execution_id=%s",
            self.execution_id,
        )

    # -----------------------------------------------------
    # Create Event
    # -----------------------------------------------------

    def record_event(
        self,
        event_type: str,
        message: str,
    ):

        event = RuntimeEvent(
            event_type=event_type,
            timestamp=time.time(),
            message=message,
        )

        self.events.append(event)

        self.monitor.record_event(event)

    # -----------------------------------------------------
    # Start Runtime
    # -----------------------------------------------------

    def start(self):

        self.monitor.start()

        self.record_event(
            "RUNTIME_STARTED",
            "Runtime execution started",
        )

    # -----------------------------------------------------
    # Execute Agent
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

            response = self.agent.run(
                user_message
            )

            response_text = response.content

            self.metrics.response_length = len(
                response_text
            )

            self.record_event(
                "AGENT_COMPLETED",
                "Agent execution completed",
            )

            return response_text

        except Exception as exc:

            self.monitor.record_error(
                str(exc)
            )

            self.record_event(
                "AGENT_FAILED",
                "Agent execution failed",
            )

            logger.exception(
                "Agent execution failed"
            )

            raise

    # -----------------------------------------------------
    # Complete Runtime
    # -----------------------------------------------------

    def complete(self):

        self.record_event(
            "RUNTIME_COMPLETED",
            "Runtime execution completed",
        )

        self.monitor.complete()


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    logger.info(
        "Starting Exercise 109"
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

    runtime.monitor.display_metrics()

    logger.info(
        "Exercise 109 completed successfully"
    )


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()