import logging
import time
import uuid
from dataclasses import dataclass
from queue import Queue, Empty
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

logger = logging.getLogger("agent_runtime_execution_queue")


# ---------------------------------------------------------
# Execution Job
# ---------------------------------------------------------

@dataclass
class ExecutionJob:
    job_id: str
    user_message: str
    status: str = "QUEUED"
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: float = 0.0
    started_at: Optional[float] = None
    completed_at: Optional[float] = None


# ---------------------------------------------------------
# Agent Runtime
# ---------------------------------------------------------

class AgentRuntime:

    def __init__(self):

        self.agent = Agent(
            model=Ollama(id="llama3.2"),
            instructions=[
                "You are a helpful AI assistant.",
                "Give clear and concise answers.",
            ],
        )

        logger.info(
            "Agent runtime initialized"
        )

    # -----------------------------------------------------
    # Execute Job
    # -----------------------------------------------------

    def execute(self, job: ExecutionJob):

        logger.info(
            "Starting job | job_id=%s",
            job.job_id,
        )

        job.status = "RUNNING"
        job.started_at = time.time()

        try:

            logger.info(
                "Sending job to agent | job_id=%s | message=%s",
                job.job_id,
                job.user_message,
            )

            response = self.agent.run(
                job.user_message
            )

            job.result = response.content
            job.status = "COMPLETED"
            job.completed_at = time.time()

            duration = (
                job.completed_at
                - job.started_at
            )

            logger.info(
                "Job completed | job_id=%s | duration=%.2f seconds",
                job.job_id,
                duration,
            )

        except Exception as exc:

            job.status = "FAILED"
            job.error = str(exc)
            job.completed_at = time.time()

            logger.exception(
                "Job failed | job_id=%s | error=%s",
                job.job_id,
                exc,
            )


# ---------------------------------------------------------
# Runtime Execution Queue
# ---------------------------------------------------------

class RuntimeExecutionQueue:

    def __init__(self):

        self.queue = Queue()
        self.jobs = {}

        logger.info(
            "Execution queue initialized"
        )

    # -----------------------------------------------------
    # Add Job
    # -----------------------------------------------------

    def add_job(self, user_message: str) -> str:

        job_id = str(uuid.uuid4())

        job = ExecutionJob(
            job_id=job_id,
            user_message=user_message,
            created_at=time.time(),
        )

        self.jobs[job_id] = job

        self.queue.put(job)

        logger.info(
            "Job added to queue | job_id=%s | queue_size=%s",
            job_id,
            self.queue.qsize(),
        )

        return job_id

    # -----------------------------------------------------
    # Process Queue
    # -----------------------------------------------------

    def process_queue(self, runtime: AgentRuntime):

        logger.info(
            "Queue processing started | pending_jobs=%s",
            self.queue.qsize(),
        )

        while True:

            try:

                job = self.queue.get_nowait()

            except Empty:

                logger.info(
                    "Execution queue is empty"
                )

                break

            logger.info(
                "Dequeued job | job_id=%s | remaining_jobs=%s",
                job.job_id,
                self.queue.qsize(),
            )

            runtime.execute(job)

            self.queue.task_done()

        logger.info(
            "Queue processing completed"
        )

    # -----------------------------------------------------
    # Display Queue Status
    # -----------------------------------------------------

    def display_status(self):

        print("\n" + "=" * 75)
        print("RUNTIME EXECUTION QUEUE REPORT")
        print("=" * 75)

        print(
            f"Pending Jobs : {self.queue.qsize()}"
        )

        print(
            f"Total Jobs   : {len(self.jobs)}"
        )

        print("-" * 75)

        for job in self.jobs.values():

            print(
                f"Job ID : {job.job_id}"
            )

            print(
                f"Status : {job.status}"
            )

            print(
                f"Request: {job.user_message}"
            )

            if job.result:

                print(
                    f"Result : {job.result[:150]}"
                )

            if job.error:

                print(
                    f"Error  : {job.error}"
                )

            print("-" * 75)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    logger.info(
        "Starting Exercise 111"
    )

    runtime = AgentRuntime()

    execution_queue = RuntimeExecutionQueue()

    # -----------------------------------------------------
    # Add multiple requests
    # -----------------------------------------------------

    requests = [
        "What is an AI agent?",
        "What is machine learning?",
        "What is an API?",
    ]

    for request in requests:

        execution_queue.add_job(request)

    # -----------------------------------------------------
    # Process queued requests
    # -----------------------------------------------------

    execution_queue.process_queue(
        runtime
    )

    # -----------------------------------------------------
    # Display final queue status
    # -----------------------------------------------------

    execution_queue.display_status()

    logger.info(
        "Exercise 111 completed successfully"
    )


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()