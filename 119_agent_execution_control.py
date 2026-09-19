import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, Optional


# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agent_execution_control")


# ---------------------------------------------------------
# Execution Status
# ---------------------------------------------------------

class ExecutionStatus(Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    COMPLETED = "COMPLETED"
    STOPPED = "STOPPED"
    FAILED = "FAILED"


# ---------------------------------------------------------
# Agent Status
# ---------------------------------------------------------

class AgentStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


# ---------------------------------------------------------
# Agent Execution
# ---------------------------------------------------------

@dataclass
class AgentExecution:
    execution_id: str
    agent_id: str
    agent_name: str
    request: str

    status: ExecutionStatus = ExecutionStatus.CREATED

    started_at: Optional[datetime] = None
    paused_at: Optional[datetime] = None
    resumed_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    stopped_at: Optional[datetime] = None

    execution_count: int = 0
    response: Optional[str] = None
    error: Optional[str] = None

    created_at: datetime = field(default_factory=datetime.now)


# ---------------------------------------------------------
# Agent Execution Controller
# ---------------------------------------------------------

class AgentExecutionController:

    def __init__(self):
        self.executions: Dict[str, AgentExecution] = {}

        logger.info("Agent Execution Controller initialized")

    # -----------------------------------------------------
    # Create Execution
    # -----------------------------------------------------

    def create_execution(
        self,
        agent_id: str,
        agent_name: str,
        request: str,
    ) -> str:

        execution_id = str(uuid.uuid4())

        execution = AgentExecution(
            execution_id=execution_id,
            agent_id=agent_id,
            agent_name=agent_name,
            request=request,
        )

        self.executions[execution_id] = execution

        logger.info(
            "Execution created | agent=%s | execution_id=%s",
            agent_name,
            execution_id,
        )

        return execution_id

    # -----------------------------------------------------
    # Start Execution
    # -----------------------------------------------------

    def start_execution(self, execution_id: str) -> bool:

        execution = self.executions.get(execution_id)

        if not execution:
            logger.warning(
                "Execution not found | execution_id=%s",
                execution_id,
            )
            return False

        if execution.status != ExecutionStatus.CREATED:
            logger.warning(
                "Cannot start execution | execution_id=%s | status=%s",
                execution_id,
                execution.status.value,
            )
            return False

        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.now()
        execution.execution_count += 1

        logger.info(
            "Execution started | agent=%s | execution_id=%s",
            execution.agent_name,
            execution_id,
        )

        return True

    # -----------------------------------------------------
    # Pause Execution
    # -----------------------------------------------------

    def pause_execution(self, execution_id: str) -> bool:

        execution = self.executions.get(execution_id)

        if not execution:
            logger.warning(
                "Execution not found | execution_id=%s",
                execution_id,
            )
            return False

        if execution.status != ExecutionStatus.RUNNING:
            logger.warning(
                "Cannot pause execution | execution_id=%s | status=%s",
                execution_id,
                execution.status.value,
            )
            return False

        execution.status = ExecutionStatus.PAUSED
        execution.paused_at = datetime.now()

        logger.info(
            "Execution paused | agent=%s | execution_id=%s",
            execution.agent_name,
            execution_id,
        )

        return True

    # -----------------------------------------------------
    # Resume Execution
    # -----------------------------------------------------

    def resume_execution(self, execution_id: str) -> bool:

        execution = self.executions.get(execution_id)

        if not execution:
            logger.warning(
                "Execution not found | execution_id=%s",
                execution_id,
            )
            return False

        if execution.status != ExecutionStatus.PAUSED:
            logger.warning(
                "Cannot resume execution | execution_id=%s | status=%s",
                execution_id,
                execution.status.value,
            )
            return False

        execution.status = ExecutionStatus.RUNNING
        execution.resumed_at = datetime.now()

        logger.info(
            "Execution resumed | agent=%s | execution_id=%s",
            execution.agent_name,
            execution_id,
        )

        return True

    # -----------------------------------------------------
    # Complete Execution
    # -----------------------------------------------------

    def complete_execution(
        self,
        execution_id: str,
        response: str,
    ) -> bool:

        execution = self.executions.get(execution_id)

        if not execution:
            logger.warning(
                "Execution not found | execution_id=%s",
                execution_id,
            )
            return False

        if execution.status != ExecutionStatus.RUNNING:
            logger.warning(
                "Cannot complete execution | execution_id=%s | status=%s",
                execution_id,
                execution.status.value,
            )
            return False

        execution.status = ExecutionStatus.COMPLETED
        execution.completed_at = datetime.now()
        execution.response = response

        logger.info(
            "Execution completed | agent=%s | execution_id=%s",
            execution.agent_name,
            execution_id,
        )

        return True

    # -----------------------------------------------------
    # Stop Execution
    # -----------------------------------------------------

    def stop_execution(self, execution_id: str) -> bool:

        execution = self.executions.get(execution_id)

        if not execution:
            logger.warning(
                "Execution not found | execution_id=%s",
                execution_id,
            )
            return False

        if execution.status not in (
            ExecutionStatus.RUNNING,
            ExecutionStatus.PAUSED,
        ):
            logger.warning(
                "Cannot stop execution | execution_id=%s | status=%s",
                execution_id,
                execution.status.value,
            )
            return False

        execution.status = ExecutionStatus.STOPPED
        execution.stopped_at = datetime.now()

        logger.info(
            "Execution stopped | agent=%s | execution_id=%s",
            execution.agent_name,
            execution_id,
        )

        return True

    # -----------------------------------------------------
    # Fail Execution
    # -----------------------------------------------------

    def fail_execution(
        self,
        execution_id: str,
        error: str,
    ) -> bool:

        execution = self.executions.get(execution_id)

        if not execution:
            logger.warning(
                "Execution not found | execution_id=%s",
                execution_id,
            )
            return False

        if execution.status not in (
            ExecutionStatus.RUNNING,
            ExecutionStatus.PAUSED,
        ):
            logger.warning(
                "Cannot fail execution | execution_id=%s | status=%s",
                execution_id,
                execution.status.value,
            )
            return False

        execution.status = ExecutionStatus.FAILED
        execution.error = error

        logger.error(
            "Execution failed | agent=%s | execution_id=%s | error=%s",
            execution.agent_name,
            execution_id,
            error,
        )

        return True

    # -----------------------------------------------------
    # Get Execution
    # -----------------------------------------------------

    def get_execution(
        self,
        execution_id: str,
    ) -> Optional[AgentExecution]:

        return self.executions.get(execution_id)

    # -----------------------------------------------------
    # Display Execution
    # -----------------------------------------------------

    def display_execution(self, execution_id: str) -> None:

        execution = self.executions.get(execution_id)

        if not execution:
            logger.warning(
                "Execution not found | execution_id=%s",
                execution_id,
            )
            return

        print("\n" + "=" * 65)
        print("AGENT EXECUTION DETAILS")
        print("=" * 65)

        print(f"Execution ID     : {execution.execution_id}")
        print(f"Agent ID         : {execution.agent_id}")
        print(f"Agent Name       : {execution.agent_name}")
        print(f"Request          : {execution.request}")
        print(f"Status           : {execution.status.value}")
        print(f"Execution Count  : {execution.execution_count}")
        print(f"Created At       : {execution.created_at}")
        print(f"Started At       : {execution.started_at}")
        print(f"Paused At        : {execution.paused_at}")
        print(f"Resumed At       : {execution.resumed_at}")
        print(f"Completed At     : {execution.completed_at}")
        print(f"Stopped At       : {execution.stopped_at}")
        print(f"Response         : {execution.response}")
        print(f"Error            : {execution.error}")

        print("=" * 65)

    # -----------------------------------------------------
    # Display All Executions
    # -----------------------------------------------------

    def display_all_executions(self) -> None:

        print("\n" + "=" * 70)
        print("AGENT EXECUTION CONTROL")
        print("=" * 70)

        if not self.executions:
            print("No executions registered")
            return

        for execution in self.executions.values():

            print(
                f"\nAgent          : {execution.agent_name}"
                f"\nExecution ID   : {execution.execution_id}"
                f"\nStatus         : {execution.status.value}"
                f"\nExecutions     : {execution.execution_count}"
            )

        print("=" * 70)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    logger.info(
        "Starting Exercise 119 - Agent Execution Control"
    )

    controller = AgentExecutionController()

    # -----------------------------------------------------
    # Create First Execution
    # -----------------------------------------------------

    execution_id = controller.create_execution(
        agent_id="agent-001",
        agent_name="AgriAssistant",
        request="Provide today's agriculture information",
    )

    # -----------------------------------------------------
    # Start Execution
    # -----------------------------------------------------

    controller.start_execution(execution_id)

    controller.display_execution(execution_id)

    # -----------------------------------------------------
    # Pause Execution
    # -----------------------------------------------------

    logger.info("Testing execution pause")

    controller.pause_execution(execution_id)

    controller.display_execution(execution_id)

    # -----------------------------------------------------
    # Resume Execution
    # -----------------------------------------------------

    logger.info("Testing execution resume")

    controller.resume_execution(execution_id)

    controller.display_execution(execution_id)

    # -----------------------------------------------------
    # Complete Execution
    # -----------------------------------------------------

    logger.info("Testing execution completion")

    time.sleep(1)

    controller.complete_execution(
        execution_id,
        "Agriculture information generated successfully.",
    )

    controller.display_execution(execution_id)

    # -----------------------------------------------------
    # Create Second Execution
    # -----------------------------------------------------

    logger.info("Creating second execution for stop test")

    second_execution_id = controller.create_execution(
        agent_id="agent-002",
        agent_name="CustomerSupportAgent",
        request="Process customer support request",
    )

    controller.start_execution(second_execution_id)

    # -----------------------------------------------------
    # Stop Second Execution
    # -----------------------------------------------------

    logger.info("Testing execution stop")

    controller.stop_execution(second_execution_id)

    controller.display_execution(second_execution_id)

    # -----------------------------------------------------
    # Create Third Execution
    # -----------------------------------------------------

    logger.info("Creating third execution for failure test")

    third_execution_id = controller.create_execution(
        agent_id="agent-003",
        agent_name="GeneralAssistant",
        request="Process general user request",
    )

    controller.start_execution(third_execution_id)

    # -----------------------------------------------------
    # Fail Third Execution
    # -----------------------------------------------------

    logger.info("Testing execution failure")

    controller.fail_execution(
        third_execution_id,
        "Simulated execution failure",
    )

    controller.display_execution(third_execution_id)

    # -----------------------------------------------------
    # Test Invalid Transition
    # -----------------------------------------------------

    logger.info("Testing invalid execution transition")

    controller.pause_execution(execution_id)

    # -----------------------------------------------------
    # Final Display
    # -----------------------------------------------------

    controller.display_all_executions()

    logger.info(
        "Exercise 119 - Agent Execution Control completed successfully"
    )


# ---------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()