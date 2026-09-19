import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agent_control_events")


# ---------------------------------------------------------
# Event Types
# ---------------------------------------------------------

class EventType(Enum):
    AGENT_REGISTERED = "AGENT_REGISTERED"
    AGENT_ACTIVATED = "AGENT_ACTIVATED"
    AGENT_DEACTIVATED = "AGENT_DEACTIVATED"

    CONFIGURATION_CREATED = "CONFIGURATION_CREATED"
    CONFIGURATION_UPDATED = "CONFIGURATION_UPDATED"

    PERMISSION_GRANTED = "PERMISSION_GRANTED"
    PERMISSION_DENIED = "PERMISSION_DENIED"

    ROUTE_SELECTED = "ROUTE_SELECTED"

    SCHEDULE_CREATED = "SCHEDULE_CREATED"
    SCHEDULE_ENABLED = "SCHEDULE_ENABLED"
    SCHEDULE_DISABLED = "SCHEDULE_DISABLED"

    EXECUTION_STARTED = "EXECUTION_STARTED"
    EXECUTION_PAUSED = "EXECUTION_PAUSED"
    EXECUTION_RESUMED = "EXECUTION_RESUMED"
    EXECUTION_COMPLETED = "EXECUTION_COMPLETED"
    EXECUTION_STOPPED = "EXECUTION_STOPPED"
    EXECUTION_FAILED = "EXECUTION_FAILED"

    HEALTH_CHECK = "HEALTH_CHECK"
    HEALTH_STATUS_CHANGED = "HEALTH_STATUS_CHANGED"


# ---------------------------------------------------------
# Event Status
# ---------------------------------------------------------

class EventStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    WARNING = "WARNING"


# ---------------------------------------------------------
# Agent Control Event
# ---------------------------------------------------------

@dataclass
class AgentControlEvent:
    event_id: str
    event_type: EventType

    agent_id: str
    agent_name: str

    status: EventStatus
    message: str

    execution_id: Optional[str] = None
    schedule_id: Optional[str] = None

    details: Dict[str, str] = field(default_factory=dict)

    created_at: datetime = field(default_factory=datetime.now)


# ---------------------------------------------------------
# Control Event Manager
# ---------------------------------------------------------

class ControlEventManager:

    def __init__(self):
        self.events: List[AgentControlEvent] = []

        logger.info("Control Event Manager initialized")

    # -----------------------------------------------------
    # Record Event
    # -----------------------------------------------------

    def record_event(
        self,
        event_type: EventType,
        agent_id: str,
        agent_name: str,
        status: EventStatus,
        message: str,
        execution_id: Optional[str] = None,
        schedule_id: Optional[str] = None,
        details: Optional[Dict[str, str]] = None,
    ) -> str:

        event_id = str(uuid.uuid4())

        event = AgentControlEvent(
            event_id=event_id,
            event_type=event_type,
            agent_id=agent_id,
            agent_name=agent_name,
            status=status,
            message=message,
            execution_id=execution_id,
            schedule_id=schedule_id,
            details=details or {},
        )

        self.events.append(event)

        logger.info(
            "Control event recorded | "
            "type=%s | agent=%s | status=%s | event_id=%s",
            event_type.value,
            agent_name,
            status.value,
            event_id,
        )

        return event_id

    # -----------------------------------------------------
    # Get Event
    # -----------------------------------------------------

    def get_event(
        self,
        event_id: str,
    ) -> Optional[AgentControlEvent]:

        for event in self.events:

            if event.event_id == event_id:
                return event

        logger.warning(
            "Event not found | event_id=%s",
            event_id,
        )

        return None

    # -----------------------------------------------------
    # Get Events By Agent
    # -----------------------------------------------------

    def get_events_by_agent(
        self,
        agent_id: str,
    ) -> List[AgentControlEvent]:

        return [
            event
            for event in self.events
            if event.agent_id == agent_id
        ]

    # -----------------------------------------------------
    # Get Events By Type
    # -----------------------------------------------------

    def get_events_by_type(
        self,
        event_type: EventType,
    ) -> List[AgentControlEvent]:

        return [
            event
            for event in self.events
            if event.event_type == event_type
        ]

    # -----------------------------------------------------
    # Get Events By Status
    # -----------------------------------------------------

    def get_events_by_status(
        self,
        status: EventStatus,
    ) -> List[AgentControlEvent]:

        return [
            event
            for event in self.events
            if event.status == status
        ]

    # -----------------------------------------------------
    # Event Count
    # -----------------------------------------------------

    def get_event_count(self) -> int:

        return len(self.events)

    # -----------------------------------------------------
    # Display Event
    # -----------------------------------------------------

    def display_event(
        self,
        event_id: str,
    ) -> None:

        event = self.get_event(event_id)

        if not event:
            return

        print("\n" + "=" * 75)
        print("CONTROL EVENT DETAILS")
        print("=" * 75)

        print(f"Event ID        : {event.event_id}")
        print(f"Event Type      : {event.event_type.value}")
        print(f"Agent ID        : {event.agent_id}")
        print(f"Agent Name      : {event.agent_name}")
        print(f"Status          : {event.status.value}")
        print(f"Message         : {event.message}")
        print(f"Execution ID    : {event.execution_id}")
        print(f"Schedule ID     : {event.schedule_id}")
        print(f"Created At      : {event.created_at}")

        print("Details         :")

        if event.details:

            for key, value in event.details.items():
                print(f"  {key}: {value}")

        else:
            print("  None")

        print("=" * 75)

    # -----------------------------------------------------
    # Display All Events
    # -----------------------------------------------------

    def display_all_events(self) -> None:

        print("\n" + "=" * 80)
        print("AGENT CONTROL EVENT HISTORY")
        print("=" * 80)

        if not self.events:
            print("No control events recorded")
            return

        for event in self.events:

            print(
                f"\nEvent ID    : {event.event_id}"
                f"\nType        : {event.event_type.value}"
                f"\nAgent       : {event.agent_name}"
                f"\nStatus      : {event.status.value}"
                f"\nMessage     : {event.message}"
                f"\nCreated At  : {event.created_at}"
            )

        print("=" * 80)

    # -----------------------------------------------------
    # Display Event Statistics
    # -----------------------------------------------------

    def display_statistics(self) -> None:

        success_count = len(
            self.get_events_by_status(
                EventStatus.SUCCESS
            )
        )

        failed_count = len(
            self.get_events_by_status(
                EventStatus.FAILED
            )
        )

        warning_count = len(
            self.get_events_by_status(
                EventStatus.WARNING
            )
        )

        print("\n" + "=" * 60)
        print("CONTROL EVENT STATISTICS")
        print("=" * 60)

        print(f"Total Events     : {self.get_event_count()}")
        print(f"Successful       : {success_count}")
        print(f"Failed           : {failed_count}")
        print(f"Warnings         : {warning_count}")

        print("=" * 60)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    logger.info(
        "Starting Exercise 121 - Agent Control Events"
    )

    manager = ControlEventManager()

    agent_id = "agent-001"
    agent_name = "AgriAssistant"

    execution_id = str(uuid.uuid4())
    schedule_id = str(uuid.uuid4())

    # -----------------------------------------------------
    # Agent Registration Event
    # -----------------------------------------------------

    registration_event_id = manager.record_event(
        event_type=EventType.AGENT_REGISTERED,
        agent_id=agent_id,
        agent_name=agent_name,
        status=EventStatus.SUCCESS,
        message="Agent registered successfully",
        details={
            "model": "llama3.2",
            "version": "1.0.0",
            "environment": "development",
        },
    )

    # -----------------------------------------------------
    # Configuration Event
    # -----------------------------------------------------

    manager.record_event(
        event_type=EventType.CONFIGURATION_CREATED,
        agent_id=agent_id,
        agent_name=agent_name,
        status=EventStatus.SUCCESS,
        message="Agent configuration created",
        details={
            "temperature": "0.3",
            "max_tokens": "2000",
        },
    )

    # -----------------------------------------------------
    # Permission Event
    # -----------------------------------------------------

    manager.record_event(
        event_type=EventType.PERMISSION_GRANTED,
        agent_id=agent_id,
        agent_name=agent_name,
        status=EventStatus.SUCCESS,
        message="Agriculture information permission granted",
        details={
            "permission": "AGRICULTURE_INFO",
        },
    )

    # -----------------------------------------------------
    # Routing Event
    # -----------------------------------------------------

    manager.record_event(
        event_type=EventType.ROUTE_SELECTED,
        agent_id=agent_id,
        agent_name=agent_name,
        status=EventStatus.SUCCESS,
        message="Agriculture request routed to AgriAssistant",
        details={
            "request_type": "AGRICULTURE",
            "priority": "1",
        },
    )

    # -----------------------------------------------------
    # Schedule Event
    # -----------------------------------------------------

    manager.record_event(
        event_type=EventType.SCHEDULE_CREATED,
        agent_id=agent_id,
        agent_name=agent_name,
        status=EventStatus.SUCCESS,
        message="Agent schedule created",
        schedule_id=schedule_id,
        details={
            "schedule_type": "INTERVAL",
            "interval_seconds": "60",
        },
    )

    # -----------------------------------------------------
    # Execution Started Event
    # -----------------------------------------------------

    manager.record_event(
        event_type=EventType.EXECUTION_STARTED,
        agent_id=agent_id,
        agent_name=agent_name,
        status=EventStatus.SUCCESS,
        message="Agent execution started",
        execution_id=execution_id,
        schedule_id=schedule_id,
        details={
            "request": "Provide agriculture information",
        },
    )

    # -----------------------------------------------------
    # Execution Paused Event
    # -----------------------------------------------------

    manager.record_event(
        event_type=EventType.EXECUTION_PAUSED,
        agent_id=agent_id,
        agent_name=agent_name,
        status=EventStatus.WARNING,
        message="Agent execution temporarily paused",
        execution_id=execution_id,
    )

    # -----------------------------------------------------
    # Execution Resumed Event
    # -----------------------------------------------------

    manager.record_event(
        event_type=EventType.EXECUTION_RESUMED,
        agent_id=agent_id,
        agent_name=agent_name,
        status=EventStatus.SUCCESS,
        message="Agent execution resumed",
        execution_id=execution_id,
    )

    # -----------------------------------------------------
    # Health Check Event
    # -----------------------------------------------------

    manager.record_event(
        event_type=EventType.HEALTH_CHECK,
        agent_id=agent_id,
        agent_name=agent_name,
        status=EventStatus.SUCCESS,
        message="Agent health check completed",
        details={
            "health_status": "HEALTHY",
            "response_time_ms": "250",
        },
    )

    # -----------------------------------------------------
    # Execution Completed Event
    # -----------------------------------------------------

    manager.record_event(
        event_type=EventType.EXECUTION_COMPLETED,
        agent_id=agent_id,
        agent_name=agent_name,
        status=EventStatus.SUCCESS,
        message="Agent execution completed successfully",
        execution_id=execution_id,
        schedule_id=schedule_id,
        details={
            "response_length": "104",
            "duration_seconds": "2.4",
        },
    )

    # -----------------------------------------------------
    # Failed Event
    # -----------------------------------------------------

    failure_event_id = manager.record_event(
        event_type=EventType.EXECUTION_FAILED,
        agent_id=agent_id,
        agent_name=agent_name,
        status=EventStatus.FAILED,
        message="Agent execution failed",
        execution_id=execution_id,
        details={
            "error": "Simulated service timeout",
        },
    )

    # -----------------------------------------------------
    # Display Individual Event
    # -----------------------------------------------------

    logger.info(
        "Displaying registration event"
    )

    manager.display_event(registration_event_id)

    # -----------------------------------------------------
    # Display Failure Event
    # -----------------------------------------------------

    logger.info(
        "Displaying failure event"
    )

    manager.display_event(failure_event_id)

    # -----------------------------------------------------
    # Query Events By Agent
    # -----------------------------------------------------

    agent_events = manager.get_events_by_agent(agent_id)

    logger.info(
        "Events found for agent=%s | count=%d",
        agent_name,
        len(agent_events),
    )

    # -----------------------------------------------------
    # Query Events By Type
    # -----------------------------------------------------

    completed_events = manager.get_events_by_type(
        EventType.EXECUTION_COMPLETED
    )

    logger.info(
        "Execution completed events found | count=%d",
        len(completed_events),
    )

    # -----------------------------------------------------
    # Query Failed Events
    # -----------------------------------------------------

    failed_events = manager.get_events_by_status(
        EventStatus.FAILED
    )

    logger.info(
        "Failed events found | count=%d",
        len(failed_events),
    )

    # -----------------------------------------------------
    # Display Complete History
    # -----------------------------------------------------

    manager.display_all_events()

    # -----------------------------------------------------
    # Display Statistics
    # -----------------------------------------------------

    manager.display_statistics()

    logger.info(
        "Exercise 121 - Agent Control Events "
        "completed successfully"
    )


# ---------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()