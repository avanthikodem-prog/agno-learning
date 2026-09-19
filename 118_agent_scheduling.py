import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agent_scheduling")


# ---------------------------------------------------------
# Agent Status
# ---------------------------------------------------------

class AgentStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


# ---------------------------------------------------------
# Schedule Type
# ---------------------------------------------------------

class ScheduleType(Enum):
    ONCE = "ONCE"
    INTERVAL = "INTERVAL"


# ---------------------------------------------------------
# Scheduled Agent
# ---------------------------------------------------------

@dataclass
class ScheduledAgent:
    schedule_id: str
    agent_id: str
    agent_name: str
    schedule_type: ScheduleType
    scheduled_time: Optional[datetime] = None
    interval_seconds: Optional[int] = None
    enabled: bool = True
    status: AgentStatus = AgentStatus.ACTIVE
    execution_count: int = 0
    last_executed_at: Optional[datetime] = None
    next_execution_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


# ---------------------------------------------------------
# Agent Scheduler
# ---------------------------------------------------------

class AgentScheduler:

    def __init__(self):
        self.schedules: Dict[str, ScheduledAgent] = {}
        logger.info("Agent Scheduler initialized")

    # -----------------------------------------------------
    # Create One-Time Schedule
    # -----------------------------------------------------

    def schedule_once(
        self,
        agent_id: str,
        agent_name: str,
        scheduled_time: datetime,
    ) -> str:

        schedule_id = str(uuid.uuid4())

        schedule = ScheduledAgent(
            schedule_id=schedule_id,
            agent_id=agent_id,
            agent_name=agent_name,
            schedule_type=ScheduleType.ONCE,
            scheduled_time=scheduled_time,
            next_execution_at=scheduled_time,
        )

        self.schedules[schedule_id] = schedule

        logger.info(
            "One-time schedule created | agent=%s | schedule_id=%s | time=%s",
            agent_name,
            schedule_id,
            scheduled_time.strftime("%Y-%m-%d %H:%M:%S"),
        )

        return schedule_id

    # -----------------------------------------------------
    # Create Interval Schedule
    # -----------------------------------------------------

    def schedule_interval(
        self,
        agent_id: str,
        agent_name: str,
        interval_seconds: int,
    ) -> str:

        if interval_seconds <= 0:
            raise ValueError("Interval must be greater than 0 seconds")

        schedule_id = str(uuid.uuid4())

        next_execution = datetime.now() + timedelta(
            seconds=interval_seconds
        )

        schedule = ScheduledAgent(
            schedule_id=schedule_id,
            agent_id=agent_id,
            agent_name=agent_name,
            schedule_type=ScheduleType.INTERVAL,
            interval_seconds=interval_seconds,
            next_execution_at=next_execution,
        )

        self.schedules[schedule_id] = schedule

        logger.info(
            "Interval schedule created | agent=%s | schedule_id=%s | interval=%s seconds",
            agent_name,
            schedule_id,
            interval_seconds,
        )

        return schedule_id

    # -----------------------------------------------------
    # Enable Schedule
    # -----------------------------------------------------

    def enable_schedule(self, schedule_id: str) -> bool:

        schedule = self.schedules.get(schedule_id)

        if not schedule:
            logger.warning(
                "Schedule not found | schedule_id=%s",
                schedule_id,
            )
            return False

        schedule.enabled = True

        logger.info(
            "Schedule enabled | schedule_id=%s | agent=%s",
            schedule_id,
            schedule.agent_name,
        )

        return True

    # -----------------------------------------------------
    # Disable Schedule
    # -----------------------------------------------------

    def disable_schedule(self, schedule_id: str) -> bool:

        schedule = self.schedules.get(schedule_id)

        if not schedule:
            logger.warning(
                "Schedule not found | schedule_id=%s",
                schedule_id,
            )
            return False

        schedule.enabled = False

        logger.info(
            "Schedule disabled | schedule_id=%s | agent=%s",
            schedule_id,
            schedule.agent_name,
        )

        return True

    # -----------------------------------------------------
    # Execute Scheduled Agent
    # -----------------------------------------------------

    def execute_schedule(self, schedule_id: str) -> bool:

        schedule = self.schedules.get(schedule_id)

        if not schedule:
            logger.warning(
                "Schedule not found | schedule_id=%s",
                schedule_id,
            )
            return False

        if not schedule.enabled:
            logger.warning(
                "Schedule is disabled | schedule_id=%s",
                schedule_id,
            )
            return False

        if schedule.status != AgentStatus.ACTIVE:
            logger.warning(
                "Agent is inactive | agent=%s",
                schedule.agent_name,
            )
            return False

        current_time = datetime.now()

        logger.info(
            "Executing scheduled agent | agent=%s | schedule_id=%s",
            schedule.agent_name,
            schedule_id,
        )

        # Simulated agent execution
        time.sleep(1)

        schedule.execution_count += 1
        schedule.last_executed_at = current_time

        # Calculate next execution
        if schedule.schedule_type == ScheduleType.ONCE:

            schedule.next_execution_at = None
            schedule.enabled = False

            logger.info(
                "One-time schedule completed | agent=%s",
                schedule.agent_name,
            )

        elif schedule.schedule_type == ScheduleType.INTERVAL:

            schedule.next_execution_at = (
                current_time
                + timedelta(seconds=schedule.interval_seconds)
            )

            logger.info(
                "Next execution scheduled | agent=%s | next=%s",
                schedule.agent_name,
                schedule.next_execution_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            )

        return True

    # -----------------------------------------------------
    # Get Schedule
    # -----------------------------------------------------

    def get_schedule(
        self,
        schedule_id: str,
    ) -> Optional[ScheduledAgent]:

        return self.schedules.get(schedule_id)

    # -----------------------------------------------------
    # List Schedules
    # -----------------------------------------------------

    def list_schedules(self) -> List[ScheduledAgent]:

        return list(self.schedules.values())

    # -----------------------------------------------------
    # Display Schedule
    # -----------------------------------------------------

    def display_schedule(self, schedule_id: str) -> None:

        schedule = self.schedules.get(schedule_id)

        if not schedule:
            logger.warning(
                "Schedule not found | schedule_id=%s",
                schedule_id,
            )
            return

        print("\n" + "=" * 60)
        print("SCHEDULE DETAILS")
        print("=" * 60)

        print(f"Schedule ID      : {schedule.schedule_id}")
        print(f"Agent ID         : {schedule.agent_id}")
        print(f"Agent Name       : {schedule.agent_name}")
        print(f"Schedule Type    : {schedule.schedule_type.value}")
        print(f"Enabled          : {schedule.enabled}")
        print(f"Status           : {schedule.status.value}")
        print(f"Execution Count  : {schedule.execution_count}")
        print(f"Created At       : {schedule.created_at}")

        if schedule.scheduled_time:
            print(f"Scheduled Time   : {schedule.scheduled_time}")

        if schedule.interval_seconds:
            print(
                f"Interval         : "
                f"{schedule.interval_seconds} seconds"
            )

        print(f"Last Executed    : {schedule.last_executed_at}")
        print(f"Next Execution   : {schedule.next_execution_at}")

        print("=" * 60)

    # -----------------------------------------------------
    # Display All Schedules
    # -----------------------------------------------------

    def display_all_schedules(self) -> None:

        print("\n" + "=" * 70)
        print("AGENT SCHEDULER")
        print("=" * 70)

        if not self.schedules:
            print("No schedules registered")
            return

        for schedule in self.schedules.values():

            print(
                f"\nAgent: {schedule.agent_name}"
                f"\nSchedule ID: {schedule.schedule_id}"
                f"\nType: {schedule.schedule_type.value}"
                f"\nEnabled: {schedule.enabled}"
                f"\nExecutions: {schedule.execution_count}"
                f"\nNext Execution: {schedule.next_execution_at}"
            )

        print("=" * 70)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    logger.info("Starting Exercise 118 - Agent Scheduling")

    scheduler = AgentScheduler()

    # -----------------------------------------------------
    # Register One-Time Schedule
    # -----------------------------------------------------

    once_time = datetime.now() + timedelta(seconds=2)

    once_schedule_id = scheduler.schedule_once(
        agent_id="agent-001",
        agent_name="AgriAssistant",
        scheduled_time=once_time,
    )

    # -----------------------------------------------------
    # Register Interval Schedule
    # -----------------------------------------------------

    interval_schedule_id = scheduler.schedule_interval(
        agent_id="agent-002",
        agent_name="CustomerSupportAgent",
        interval_seconds=3,
    )

    # -----------------------------------------------------
    # Display Schedules
    # -----------------------------------------------------

    scheduler.display_all_schedules()

    # -----------------------------------------------------
    # Execute One-Time Schedule
    # -----------------------------------------------------

    logger.info("Waiting for one-time schedule...")

    time.sleep(2)

    scheduler.execute_schedule(once_schedule_id)

    scheduler.display_schedule(once_schedule_id)

    # -----------------------------------------------------
    # Execute Interval Schedule
    # -----------------------------------------------------

    logger.info("Executing interval schedule")

    scheduler.execute_schedule(interval_schedule_id)

    scheduler.display_schedule(interval_schedule_id)

    # -----------------------------------------------------
    # Disable Schedule
    # -----------------------------------------------------

    logger.info("Testing schedule disable")

    scheduler.disable_schedule(interval_schedule_id)

    scheduler.execute_schedule(interval_schedule_id)

    # -----------------------------------------------------
    # Re-enable Schedule
    # -----------------------------------------------------

    logger.info("Testing schedule re-enable")

    scheduler.enable_schedule(interval_schedule_id)

    scheduler.execute_schedule(interval_schedule_id)

    # -----------------------------------------------------
    # Final Display
    # -----------------------------------------------------

    scheduler.display_all_schedules()

    logger.info(
        "Exercise 118 - Agent Scheduling completed successfully"
    )


# ---------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()