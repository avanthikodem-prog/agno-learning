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

logger = logging.getLogger("agent_health_management")


# ---------------------------------------------------------
# Agent Health Status
# ---------------------------------------------------------

class HealthStatus(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


# ---------------------------------------------------------
# Agent Status
# ---------------------------------------------------------

class AgentStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


# ---------------------------------------------------------
# Agent Health Information
# ---------------------------------------------------------

@dataclass
class AgentHealth:
    health_id: str
    agent_id: str
    agent_name: str

    status: HealthStatus = HealthStatus.UNKNOWN
    agent_status: AgentStatus = AgentStatus.ACTIVE

    last_heartbeat: Optional[datetime] = None

    response_time_ms: float = 0.0

    successful_executions: int = 0
    failed_executions: int = 0
    error_count: int = 0

    uptime_seconds: float = 0.0

    health_checks: int = 0
    healthy_checks: int = 0
    unhealthy_checks: int = 0

    started_at: datetime = field(default_factory=datetime.now)

    last_error: Optional[str] = None


# ---------------------------------------------------------
# Agent Health Manager
# ---------------------------------------------------------

class AgentHealthManager:

    def __init__(self):
        self.agents: Dict[str, AgentHealth] = {}

        logger.info("Agent Health Manager initialized")

    # -----------------------------------------------------
    # Register Agent
    # -----------------------------------------------------

    def register_agent(
        self,
        agent_id: str,
        agent_name: str,
    ) -> str:

        health_id = str(uuid.uuid4())

        health = AgentHealth(
            health_id=health_id,
            agent_id=agent_id,
            agent_name=agent_name,
        )

        self.agents[agent_id] = health

        logger.info(
            "Agent health monitoring registered | "
            "agent=%s | health_id=%s",
            agent_name,
            health_id,
        )

        return health_id

    # -----------------------------------------------------
    # Heartbeat
    # -----------------------------------------------------

    def heartbeat(self, agent_id: str) -> bool:

        health = self.agents.get(agent_id)

        if not health:
            logger.warning(
                "Agent not found for heartbeat | agent_id=%s",
                agent_id,
            )
            return False

        health.last_heartbeat = datetime.now()

        logger.info(
            "Heartbeat received | agent=%s | time=%s",
            health.agent_name,
            health.last_heartbeat.strftime(
                "%Y-%m-%d %H:%M:%S"
            ),
        )

        return True

    # -----------------------------------------------------
    # Record Successful Execution
    # -----------------------------------------------------

    def record_success(
        self,
        agent_id: str,
        response_time_ms: float,
    ) -> bool:

        health = self.agents.get(agent_id)

        if not health:
            logger.warning(
                "Agent not found | agent_id=%s",
                agent_id,
            )
            return False

        health.successful_executions += 1
        health.response_time_ms = response_time_ms

        logger.info(
            "Successful execution recorded | "
            "agent=%s | response_time=%.2f ms",
            health.agent_name,
            response_time_ms,
        )

        return True

    # -----------------------------------------------------
    # Record Failed Execution
    # -----------------------------------------------------

    def record_failure(
        self,
        agent_id: str,
        error: str,
    ) -> bool:

        health = self.agents.get(agent_id)

        if not health:
            logger.warning(
                "Agent not found | agent_id=%s",
                agent_id,
            )
            return False

        health.failed_executions += 1
        health.error_count += 1
        health.last_error = error

        logger.error(
            "Failed execution recorded | "
            "agent=%s | error=%s",
            health.agent_name,
            error,
        )

        return True

    # -----------------------------------------------------
    # Calculate Uptime
    # -----------------------------------------------------

    def calculate_uptime(self, agent_id: str) -> float:

        health = self.agents.get(agent_id)

        if not health:
            logger.warning(
                "Agent not found | agent_id=%s",
                agent_id,
            )
            return 0.0

        health.uptime_seconds = (
            datetime.now() - health.started_at
        ).total_seconds()

        return health.uptime_seconds

    # -----------------------------------------------------
    # Health Check
    # -----------------------------------------------------

    def health_check(self, agent_id: str) -> HealthStatus:

        health = self.agents.get(agent_id)

        if not health:
            logger.warning(
                "Agent not found for health check | agent_id=%s",
                agent_id,
            )
            return HealthStatus.UNKNOWN

        health.health_checks += 1

        current_time = datetime.now()

        # ---------------------------------------------
        # No heartbeat means unknown
        # ---------------------------------------------

        if health.last_heartbeat is None:

            health.status = HealthStatus.UNKNOWN
            health.unhealthy_checks += 1

            logger.warning(
                "Health check failed | "
                "agent=%s | reason=no heartbeat",
                health.agent_name,
            )

            return health.status

        # ---------------------------------------------
        # Heartbeat age
        # ---------------------------------------------

        heartbeat_age = (
            current_time - health.last_heartbeat
        ).total_seconds()

        # ---------------------------------------------
        # Unhealthy conditions
        # ---------------------------------------------

        if (
            health.agent_status == AgentStatus.INACTIVE
            or heartbeat_age > 10
            or health.failed_executions >= 3
        ):

            health.status = HealthStatus.UNHEALTHY
            health.unhealthy_checks += 1

            logger.warning(
                "Agent health status changed | "
                "agent=%s | status=UNHEALTHY",
                health.agent_name,
            )

        # ---------------------------------------------
        # Degraded conditions
        # ---------------------------------------------

        elif (
            heartbeat_age > 5
            or health.response_time_ms > 1000
            or health.error_count >= 1
        ):

            health.status = HealthStatus.DEGRADED
            health.unhealthy_checks += 1

            logger.warning(
                "Agent health status changed | "
                "agent=%s | status=DEGRADED",
                health.agent_name,
            )

        # ---------------------------------------------
        # Healthy
        # ---------------------------------------------

        else:

            health.status = HealthStatus.HEALTHY
            health.healthy_checks += 1

            logger.info(
                "Agent health status changed | "
                "agent=%s | status=HEALTHY",
                health.agent_name,
            )

        return health.status

    # -----------------------------------------------------
    # Set Agent Status
    # -----------------------------------------------------

    def set_agent_status(
        self,
        agent_id: str,
        status: AgentStatus,
    ) -> bool:

        health = self.agents.get(agent_id)

        if not health:
            logger.warning(
                "Agent not found | agent_id=%s",
                agent_id,
            )
            return False

        health.agent_status = status

        logger.info(
            "Agent status updated | "
            "agent=%s | status=%s",
            health.agent_name,
            status.value,
        )

        return True

    # -----------------------------------------------------
    # Get Health
    # -----------------------------------------------------

    def get_health(
        self,
        agent_id: str,
    ) -> Optional[AgentHealth]:

        return self.agents.get(agent_id)

    # -----------------------------------------------------
    # Display Health
    # -----------------------------------------------------

    def display_health(self, agent_id: str) -> None:

        health = self.agents.get(agent_id)

        if not health:
            logger.warning(
                "Agent not found | agent_id=%s",
                agent_id,
            )
            return

        self.calculate_uptime(agent_id)

        print("\n" + "=" * 70)
        print("AGENT HEALTH DETAILS")
        print("=" * 70)

        print(f"Health ID          : {health.health_id}")
        print(f"Agent ID           : {health.agent_id}")
        print(f"Agent Name         : {health.agent_name}")
        print(f"Agent Status       : {health.agent_status.value}")
        print(f"Health Status      : {health.status.value}")
        print(f"Last Heartbeat     : {health.last_heartbeat}")
        print(
            f"Response Time      : "
            f"{health.response_time_ms:.2f} ms"
        )
        print(
            f"Successful Runs    : "
            f"{health.successful_executions}"
        )
        print(
            f"Failed Runs        : "
            f"{health.failed_executions}"
        )
        print(f"Error Count        : {health.error_count}")
        print(
            f"Uptime             : "
            f"{health.uptime_seconds:.2f} seconds"
        )
        print(f"Health Checks      : {health.health_checks}")
        print(f"Healthy Checks     : {health.healthy_checks}")
        print(
            f"Unhealthy Checks   : "
            f"{health.unhealthy_checks}"
        )
        print(f"Last Error         : {health.last_error}")

        print("=" * 70)

    # -----------------------------------------------------
    # Display All Agents
    # -----------------------------------------------------

    def display_all_health(self) -> None:

        print("\n" + "=" * 75)
        print("AGENT HEALTH MANAGEMENT")
        print("=" * 75)

        if not self.agents:
            print("No agents registered")
            return

        for health in self.agents.values():

            self.calculate_uptime(health.agent_id)

            print(
                f"\nAgent            : {health.agent_name}"
                f"\nAgent ID         : {health.agent_id}"
                f"\nAgent Status     : {health.agent_status.value}"
                f"\nHealth Status    : {health.status.value}"
                f"\nResponse Time    : "
                f"{health.response_time_ms:.2f} ms"
                f"\nSuccessful Runs  : "
                f"{health.successful_executions}"
                f"\nFailed Runs      : "
                f"{health.failed_executions}"
                f"\nError Count      : {health.error_count}"
                f"\nUptime           : "
                f"{health.uptime_seconds:.2f} seconds"
            )

        print("=" * 75)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    logger.info(
        "Starting Exercise 120 - Agent Health Management"
    )

    manager = AgentHealthManager()

    # -----------------------------------------------------
    # Register AgriAssistant
    # -----------------------------------------------------

    manager.register_agent(
        agent_id="agent-001",
        agent_name="AgriAssistant",
    )

    # -----------------------------------------------------
    # Register CustomerSupportAgent
    # -----------------------------------------------------

    manager.register_agent(
        agent_id="agent-002",
        agent_name="CustomerSupportAgent",
    )

    # -----------------------------------------------------
    # Test Healthy Agent
    # -----------------------------------------------------

    logger.info("Testing healthy agent")

    manager.heartbeat("agent-001")

    manager.record_success(
        agent_id="agent-001",
        response_time_ms=250.0,
    )

    manager.health_check("agent-001")

    manager.display_health("agent-001")

    # -----------------------------------------------------
    # Test Degraded Agent
    # -----------------------------------------------------

    logger.info("Testing degraded agent")

    manager.heartbeat("agent-002")

    manager.record_success(
        agent_id="agent-002",
        response_time_ms=1500.0,
    )

    manager.record_failure(
        agent_id="agent-002",
        error="Temporary service timeout",
    )

    manager.health_check("agent-002")

    manager.display_health("agent-002")

    # -----------------------------------------------------
    # Test Unhealthy Agent
    # -----------------------------------------------------

    logger.info("Testing unhealthy agent")

    manager.record_failure(
        agent_id="agent-002",
        error="Service unavailable",
    )

    manager.record_failure(
        agent_id="agent-002",
        error="Repeated execution failure",
    )

    manager.health_check("agent-002")

    manager.display_health("agent-002")

    # -----------------------------------------------------
    # Test Inactive Agent
    # -----------------------------------------------------

    logger.info("Testing inactive agent")

    manager.set_agent_status(
        agent_id="agent-002",
        status=AgentStatus.INACTIVE,
    )

    manager.health_check("agent-002")

    manager.display_health("agent-002")

    # -----------------------------------------------------
    # Final Health Report
    # -----------------------------------------------------

    manager.display_all_health()

    logger.info(
        "Exercise 120 - Agent Health Management "
        "completed successfully"
    )


# ---------------------------------------------------------
# Application Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()