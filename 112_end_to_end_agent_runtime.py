import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from queue import Queue, Empty
from typing import Optional


from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("end_to_end_agent_runtime")


# ============================================================
# RUNTIME STATUS
# ============================================================

class RuntimeStatus(Enum):
    CREATED = "CREATED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    RECOVERING = "RECOVERING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# ============================================================
# RUNTIME CONTEXT
# ============================================================

@dataclass
class RuntimeContext:
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


# ============================================================
# RUNTIME STATE
# ============================================================

@dataclass
class RuntimeState:
    execution_id: str

    status: str = RuntimeStatus.CREATED.value

    current_job_id: Optional[str] = None

    user_message: Optional[str] = None

    agent_response: Optional[str] = None

    execution_count: int = 0

    attempts: int = 0

    error: Optional[str] = None


# ============================================================
# RUNTIME EVENT
# ============================================================

@dataclass
class RuntimeEvent:
    event_id: str
    event_type: str
    execution_id: str
    timestamp: float
    message: str


# ============================================================
# RUNTIME METRICS
# ============================================================

@dataclass
class RuntimeMetrics:
    execution_id: str

    start_time: Optional[float] = None

    end_time: Optional[float] = None

    duration: float = 0.0

    event_count: int = 0

    tool_calls: int = 0

    response_length: int = 0

    attempts: int = 0

    error: Optional[str] = None


# ============================================================
# EXECUTION JOB
# ============================================================

@dataclass
class ExecutionJob:
    job_id: str

    user_message: str

    status: str = "QUEUED"

    result: Optional[str] = None

    error: Optional[str] = None

    attempts: int = 0

    created_at: float = field(
        default_factory=time.time
    )

    started_at: Optional[float] = None

    completed_at: Optional[float] = None


# ============================================================
# END-TO-END AGENT RUNTIME
# ============================================================

class EndToEndAgentRuntime:

    def __init__(self, context: RuntimeContext):

        self.context = context

        self.state = RuntimeState(
            execution_id=context.execution_id
        )

        self.metrics = RuntimeMetrics(
            execution_id=context.execution_id
        )

        self.events = []

        self.execution_queue = Queue()

        self.tool_call_count = 0

        self.max_attempts = 2

        # ----------------------------------------------------
        # Create Agno Agent
        # ----------------------------------------------------

        self.agent = Agent(
            model=Ollama(
                id="llama3.2",
                host="http://127.0.0.1:11434",
            ),
            tools=[self.add_numbers],
        )

        logger.info(
            "Agent initialized | model=llama3.2 | execution_id=%s",
            self.context.execution_id,
        )

        # ----------------------------------------------------
        # Initial Event
        # ----------------------------------------------------

        self.record_event(
            event_type="RUNTIME_CREATED",
            message="End-to-end runtime created",
        )


    # ========================================================
    # TOOL
    # ========================================================

    def add_numbers(
        self,
        a: float,
        b: float,
    ) -> float:

        self.tool_call_count += 1

        self.metrics.tool_calls = self.tool_call_count

        self.record_event(
            event_type="TOOL_STARTED",
            message=f"add_numbers called with a={a}, b={b}",
        )

        logger.info(
            "Tool called | name=add_numbers | a=%s | b=%s",
            a,
            b,
        )

        result = a + b

        logger.info(
            "Tool completed | name=add_numbers | result=%s",
            result,
        )

        self.record_event(
            event_type="TOOL_COMPLETED",
            message=f"add_numbers returned {result}",
        )

        return result


    # ========================================================
    # EVENT RECORDING
    # ========================================================

    def record_event(
        self,
        event_type: str,
        message: str,
    ):

        event = RuntimeEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            execution_id=self.context.execution_id,
            timestamp=time.time(),
            message=message,
        )

        self.events.append(event)

        self.metrics.event_count = len(self.events)

        logger.info(
            "Event recorded | type=%s | message=%s",
            event_type,
            message,
        )


    # ========================================================
    # START RUNTIME
    # ========================================================

    def start(self):

        self.state.status = RuntimeStatus.STARTING.value

        self.metrics.start_time = time.time()

        self.record_event(
            event_type="RUNTIME_STARTED",
            message="Runtime starting",
        )

        logger.info(
            "Runtime starting | execution_id=%s",
            self.context.execution_id,
        )

        self.state.status = RuntimeStatus.RUNNING.value

        self.record_event(
            event_type="RUNTIME_RUNNING",
            message="Runtime is now running",
        )


    # ========================================================
    # BUILD CONTEXT MESSAGE
    # ========================================================

    def build_context_message(
        self,
        user_message: str,
    ) -> str:

        return f"""
You are an AI assistant running inside an agent runtime.

Runtime Context:
- User Role: {self.context.user_role}
- Language: {self.context.language}
- Location: {self.context.location}
- Request Type: {self.context.request_type}
- Session ID: {self.context.session_id}
- Execution ID: {self.context.execution_id}

User Request:
{user_message}

Follow the runtime context while answering the user.

If the request requires the add_numbers tool, use the tool before
giving the final answer.
"""


    # ========================================================
    # ADD JOB TO QUEUE
    # ========================================================

    def add_job(
        self,
        user_message: str,
    ) -> ExecutionJob:

        job = ExecutionJob(
            job_id=str(uuid.uuid4()),
            user_message=user_message,
        )

        self.execution_queue.put(job)

        self.record_event(
            event_type="JOB_QUEUED",
            message=f"Job {job.job_id} added to execution queue",
        )

        logger.info(
            "Job added to queue | job_id=%s | queue_size=%s",
            job.job_id,
            self.execution_queue.qsize(),
        )

        return job


    # ========================================================
    # ERROR RECOVERY
    # ========================================================

    def recover(
        self,
        job: ExecutionJob,
        error: Exception,
    ):

        self.state.status = RuntimeStatus.RECOVERING.value

        self.state.error = str(error)

        self.metrics.error = str(error)

        self.record_event(
            event_type="RECOVERY_STARTED",
            message=f"Recovery started after error: {error}",
        )

        logger.warning(
            "Runtime recovery started | job_id=%s | error=%s",
            job.job_id,
            error,
        )

        # Clear previous error before retry
        job.error = None

        self.state.error = None

        self.metrics.error = None

        self.state.status = RuntimeStatus.RUNNING.value

        self.record_event(
            event_type="RECOVERY_COMPLETED",
            message="Recovery completed, retrying execution",
        )

        logger.info(
            "Recovery completed | retrying job_id=%s",
            job.job_id,
        )


    # ========================================================
    # EXECUTE JOB
    # ========================================================

    def execute_job(
        self,
        job: ExecutionJob,
    ):

        job.status = "RUNNING"

        job.started_at = time.time()

        self.state.current_job_id = job.job_id

        self.state.user_message = job.user_message

        self.state.execution_count += 1

        context_message = self.build_context_message(
            job.user_message
        )

        while job.attempts < self.max_attempts:

            job.attempts += 1

            self.state.attempts = job.attempts

            self.metrics.attempts = job.attempts

            logger.info(
                "Agent execution attempt | job_id=%s | attempt=%s/%s",
                job.job_id,
                job.attempts,
                self.max_attempts,
            )

            self.record_event(
                event_type="AGENT_ATTEMPT_STARTED",
                message=(
                    f"Agent attempt {job.attempts}/"
                    f"{self.max_attempts}"
                ),
            )

            try:

                # ------------------------------------------------
                # Controlled failure on first attempt
                # ------------------------------------------------

                if job.attempts == 1:

                    logger.warning(
                        "Simulating transient runtime failure "
                        "for recovery demonstration"
                    )

                    raise RuntimeError(
                        "Simulated transient runtime failure"
                    )

                # ------------------------------------------------
                # Real Agent Execution
                # ------------------------------------------------

                logger.info(
                    "Sending request to Agno agent | job_id=%s",
                    job.job_id,
                )

                response = self.agent.run(
                    context_message
                )

                result = response.content or ""

                job.result = result

                job.status = "COMPLETED"

                job.completed_at = time.time()

                self.state.agent_response = result

                self.state.status = RuntimeStatus.COMPLETED.value

                self.state.error = None

                self.metrics.error = None

                self.metrics.response_length = len(result)

                self.record_event(
                    event_type="AGENT_COMPLETED",
                    message="Agent execution completed successfully",
                )

                logger.info(
                    "Agent execution successful | job_id=%s | response_length=%s",
                    job.job_id,
                    len(result),
                )

                return

            except Exception as exc:

                job.error = str(exc)

                self.state.error = str(exc)

                self.metrics.error = str(exc)

                logger.error(
                    "Agent execution failed | job_id=%s | "
                    "attempt=%s | error=%s",
                    job.job_id,
                    job.attempts,
                    exc,
                )

                self.record_event(
                    event_type="AGENT_FAILED",
                    message=f"Agent attempt failed: {exc}",
                )

                if job.attempts < self.max_attempts:

                    self.recover(
                        job,
                        exc,
                    )

                else:

                    job.status = "FAILED"

                    job.completed_at = time.time()

                    self.state.status = RuntimeStatus.FAILED.value

                    self.record_event(
                        event_type="RUNTIME_FAILED",
                        message="Maximum execution attempts reached",
                    )

                    logger.error(
                        "Job permanently failed | job_id=%s",
                        job.job_id,
                    )

                    return


    # ========================================================
    # PROCESS QUEUE
    # ========================================================

    def process_queue(self):

        self.start()

        logger.info(
            "Starting execution queue processing"
        )

        while True:

            try:

                job = self.execution_queue.get_nowait()

            except Empty:

                break

            self.record_event(
                event_type="JOB_DEQUEUED",
                message=f"Processing job {job.job_id}",
            )

            logger.info(
                "Processing job | job_id=%s",
                job.job_id,
            )

            self.execute_job(job)

            self.execution_queue.task_done()

        # ----------------------------------------------------
        # Runtime completion
        # ----------------------------------------------------

        self.metrics.end_time = time.time()

        if self.metrics.start_time is not None:

            self.metrics.duration = (
                self.metrics.end_time
                - self.metrics.start_time
            )

        if self.state.status != RuntimeStatus.FAILED.value:

            self.state.status = RuntimeStatus.COMPLETED.value

            self.record_event(
                event_type="RUNTIME_COMPLETED",
                message="End-to-end runtime completed",
            )

        logger.info(
            "Queue processing completed | status=%s",
            self.state.status,
        )


    # ========================================================
    # DISPLAY FINAL REPORT
    # ========================================================

    def display_report(
        self,
        job: ExecutionJob,
    ):

        print("\n" + "=" * 70)
        print("END-TO-END AGENT RUNTIME REPORT")
        print("=" * 70)

        print("\nRUNTIME")
        print("-" * 70)

        print(
            f"Execution ID : {self.context.execution_id}"
        )

        print(
            f"Session ID   : {self.context.session_id}"
        )

        print(
            f"Status       : {self.state.status}"
        )

        print(
            f"Executions   : {self.state.execution_count}"
        )

        print(
            f"Attempts     : {self.state.attempts}"
        )

        print("\nCONTEXT")
        print("-" * 70)

        print(
            f"User Role    : {self.context.user_role}"
        )

        print(
            f"Language     : {self.context.language}"
        )

        print(
            f"Location     : {self.context.location}"
        )

        print(
            f"Request Type : {self.context.request_type}"
        )

        print("\nJOB")
        print("-" * 70)

        print(
            f"Job ID       : {job.job_id}"
        )

        print(
            f"Job Status   : {job.status}"
        )

        print(
            f"User Message : {job.user_message}"
        )

        print("\nMETRICS")
        print("-" * 70)

        print(
            f"Duration     : {self.metrics.duration:.2f} sec"
        )

        print(
            f"Events       : {self.metrics.event_count}"
        )

        print(
            f"Tool Calls   : {self.metrics.tool_calls}"
        )

        print(
            f"Response Len : {self.metrics.response_length}"
        )

        print(
            f"Attempts     : {self.metrics.attempts}"
        )

        print(
            f"Error        : {self.metrics.error}"
        )

        print("\nAGENT RESPONSE")
        print("-" * 70)

        if job.result:

            print(job.result)

        else:

            print("No response generated.")

        print("\nEVENT HISTORY")
        print("-" * 70)

        for index, event in enumerate(
            self.events,
            start=1,
        ):

            timestamp = time.strftime(
                "%H:%M:%S",
                time.localtime(event.timestamp),
            )

            print(
                f"{index}. "
                f"{timestamp} | "
                f"{event.event_type} | "
                f"{event.message}"
            )

        print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info(
        "Starting Exercise 112 - End-to-End Agent Runtime"
    )

    # --------------------------------------------------------
    # Create runtime context
    # --------------------------------------------------------

    context = RuntimeContext(
        user_role="customer",
        language="English",
        location="Hyderabad",
        request_type="calculation",
    )

    # --------------------------------------------------------
    # Create runtime
    # --------------------------------------------------------

    runtime = EndToEndAgentRuntime(
        context=context
    )

    # --------------------------------------------------------
    # Add job to execution queue
    # --------------------------------------------------------

    job = runtime.add_job(
        "Use the add_numbers tool to calculate "
        "125 + 75 and explain the result clearly."
    )

    # --------------------------------------------------------
    # Process queue
    # --------------------------------------------------------

    runtime.process_queue()

    # --------------------------------------------------------
    # Display final report
    # --------------------------------------------------------

    runtime.display_report(job)

    logger.info(
        "Exercise 112 completed"
    )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()