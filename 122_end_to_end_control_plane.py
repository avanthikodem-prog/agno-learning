import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("end_to_end_control_plane")


# ============================================================
# ENUMS
# ============================================================

class AgentStatus(Enum):
    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class Environment(Enum):
    DEVELOPMENT = "DEVELOPMENT"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"


class RequestType(Enum):
    AGRICULTURE = "AGRICULTURE"
    CUSTOMER_SUPPORT = "CUSTOMER_SUPPORT"
    GENERAL = "GENERAL"


class PermissionAction(Enum):
    AGRICULTURE_INFO = "AGRICULTURE_INFO"
    DATA_ANALYSIS = "DATA_ANALYSIS"
    CUSTOMER_SUPPORT = "CUSTOMER_SUPPORT"
    WEB_SEARCH = "WEB_SEARCH"


class ExecutionStatus(Enum):
    CREATED = "CREATED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class HealthStatus(Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


class EventType(Enum):
    AGENT_REGISTERED = "AGENT_REGISTERED"
    AGENT_ACTIVATED = "AGENT_ACTIVATED"
    CONFIGURATION_CREATED = "CONFIGURATION_CREATED"
    PERMISSION_GRANTED = "PERMISSION_GRANTED"
    ROUTE_SELECTED = "ROUTE_SELECTED"
    SCHEDULE_CREATED = "SCHEDULE_CREATED"
    EXECUTION_STARTED = "EXECUTION_STARTED"
    EXECUTION_COMPLETED = "EXECUTION_COMPLETED"
    HEALTH_CHECK = "HEALTH_CHECK"
    EXECUTION_FAILED = "EXECUTION_FAILED"


class EventStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    WARNING = "WARNING"


# ============================================================
# DATA MODELS
# ============================================================

@dataclass
class Agent:
    agent_id: str
    agent_name: str
    description: str
    model: str
    version: str
    capabilities: List[str]
    owner: str
    environment: Environment
    status: AgentStatus = AgentStatus.REGISTERED
    registered_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentConfiguration:
    config_id: str
    agent_id: str
    model: str
    temperature: float
    max_tokens: int
    system_prompt: str
    tools: List[str]
    language: str
    environment: Environment
    enabled: bool = True


@dataclass
class AgentPermission:
    permission_id: str
    agent_id: str
    action: PermissionAction
    allowed: bool
    granted_at: datetime = field(default_factory=datetime.now)


@dataclass
class RoutingRule:
    rule_id: str
    request_type: RequestType
    agent_id: str
    priority: int
    enabled: bool = True


@dataclass
class AgentSchedule:
    schedule_id: str
    agent_id: str
    agent_name: str
    scheduled_time: datetime
    enabled: bool = True
    execution_count: int = 0


@dataclass
class AgentExecution:
    execution_id: str
    agent_id: str
    agent_name: str
    request: str
    status: ExecutionStatus = ExecutionStatus.CREATED
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    response: Optional[str] = None
    error: Optional[str] = None


@dataclass
class AgentHealth:
    health_id: str
    agent_id: str
    agent_name: str
    status: HealthStatus = HealthStatus.UNKNOWN
    last_heartbeat: Optional[datetime] = None
    response_time_ms: float = 0.0
    successful_executions: int = 0
    failed_executions: int = 0
    error_count: int = 0


@dataclass
class ControlEvent:
    event_id: str
    event_type: EventType
    agent_id: str
    agent_name: str
    status: EventStatus
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    execution_id: Optional[str] = None
    schedule_id: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)


# ============================================================
# CONTROL PLANE
# ============================================================

class EndToEndControlPlane:

    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.configurations: Dict[str, AgentConfiguration] = {}
        self.permissions: List[AgentPermission] = []
        self.routing_rules: List[RoutingRule] = []
        self.schedules: Dict[str, AgentSchedule] = {}
        self.executions: Dict[str, AgentExecution] = {}
        self.health: Dict[str, AgentHealth] = {}
        self.events: List[ControlEvent] = []

        logger.info("End-to-End Control Plane initialized")

    # ========================================================
    # EVENT MANAGEMENT
    # ========================================================

    def record_event(
        self,
        event_type: EventType,
        agent: Agent,
        status: EventStatus,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        execution_id: Optional[str] = None,
        schedule_id: Optional[str] = None,
    ) -> ControlEvent:

        event = ControlEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            agent_id=agent.agent_id,
            agent_name=agent.agent_name,
            status=status,
            message=message,
            details=details or {},
            execution_id=execution_id,
            schedule_id=schedule_id,
        )

        self.events.append(event)

        logger.info(
            "Control event recorded | type=%s | agent=%s | status=%s | event_id=%s",
            event_type.value,
            agent.agent_name,
            status.value,
            event.event_id,
        )

        return event

    # ========================================================
    # 1. AGENT REGISTRATION
    # ========================================================

    def register_agent(
        self,
        agent_name: str,
        description: str,
        model: str,
        capabilities: List[str],
        owner: str,
        environment: Environment,
    ) -> Agent:

        agent = Agent(
            agent_id=str(uuid.uuid4()),
            agent_name=agent_name,
            description=description,
            model=model,
            version="1.0.0",
            capabilities=capabilities,
            owner=owner,
            environment=environment,
        )

        self.agents[agent.agent_id] = agent

        logger.info(
            "Agent registered | name=%s | agent_id=%s",
            agent.agent_name,
            agent.agent_id,
        )

        self.record_event(
            EventType.AGENT_REGISTERED,
            agent,
            EventStatus.SUCCESS,
            "Agent registered successfully",
            {
                "model": agent.model,
                "version": agent.version,
                "environment": agent.environment.value,
            },
        )

        return agent

    # ========================================================
    # 2. AGENT ACTIVATION
    # ========================================================

    def activate_agent(self, agent_id: str) -> bool:

        agent = self.agents.get(agent_id)

        if not agent:
            logger.error("Agent not found | agent_id=%s", agent_id)
            return False

        agent.status = AgentStatus.ACTIVE

        logger.info("Agent activated | name=%s", agent.agent_name)

        self.record_event(
            EventType.AGENT_ACTIVATED,
            agent,
            EventStatus.SUCCESS,
            "Agent activated successfully",
        )

        return True

    # ========================================================
    # 3. CONFIGURATION
    # ========================================================

    def create_configuration(
        self,
        agent: Agent,
        temperature: float,
        max_tokens: int,
        tools: List[str],
        language: str,
    ) -> AgentConfiguration:

        configuration = AgentConfiguration(
            config_id=str(uuid.uuid4()),
            agent_id=agent.agent_id,
            model=agent.model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=(
                "You are an AI assistant that provides helpful and "
                "accurate information."
            ),
            tools=tools,
            language=language,
            environment=agent.environment,
        )

        self.configurations[agent.agent_id] = configuration

        logger.info(
            "Configuration created | agent=%s | config_id=%s",
            agent.agent_name,
            configuration.config_id,
        )

        self.record_event(
            EventType.CONFIGURATION_CREATED,
            agent,
            EventStatus.SUCCESS,
            "Agent configuration created",
            {
                "temperature": temperature,
                "max_tokens": max_tokens,
                "tools": tools,
                "language": language,
            },
        )

        return configuration

    # ========================================================
    # 4. PERMISSIONS
    # ========================================================

    def grant_permission(
        self,
        agent: Agent,
        action: PermissionAction,
    ) -> AgentPermission:

        permission = AgentPermission(
            permission_id=str(uuid.uuid4()),
            agent_id=agent.agent_id,
            action=action,
            allowed=True,
        )

        self.permissions.append(permission)

        logger.info(
            "Permission granted | agent=%s | action=%s",
            agent.agent_name,
            action.value,
        )

        self.record_event(
            EventType.PERMISSION_GRANTED,
            agent,
            EventStatus.SUCCESS,
            f"{action.value} permission granted",
        )

        return permission

    # ========================================================
    # 5. ROUTING
    # ========================================================

    def add_routing_rule(
        self,
        request_type: RequestType,
        agent: Agent,
        priority: int,
    ) -> RoutingRule:

        rule = RoutingRule(
            rule_id=str(uuid.uuid4()),
            request_type=request_type,
            agent_id=agent.agent_id,
            priority=priority,
        )

        self.routing_rules.append(rule)

        logger.info(
            "Routing rule added | request=%s | agent=%s",
            request_type.value,
            agent.agent_name,
        )

        return rule

    def route_request(
        self,
        request_type: RequestType,
    ) -> Optional[Agent]:

        matching_rules = [
            rule
            for rule in self.routing_rules
            if rule.request_type == request_type
            and rule.enabled
        ]

        matching_rules.sort(key=lambda rule: rule.priority)

        if not matching_rules:
            logger.warning(
                "No routing rule found | request=%s",
                request_type.value,
            )
            return None

        rule = matching_rules[0]
        agent = self.agents.get(rule.agent_id)

        if not agent or agent.status != AgentStatus.ACTIVE:
            logger.warning(
                "No active agent available | request=%s",
                request_type.value,
            )
            return None

        logger.info(
            "Request routed | request=%s | agent=%s",
            request_type.value,
            agent.agent_name,
        )

        self.record_event(
            EventType.ROUTE_SELECTED,
            agent,
            EventStatus.SUCCESS,
            f"{request_type.value} request routed to {agent.agent_name}",
            {
                "request_type": request_type.value,
                "priority": rule.priority,
            },
        )

        return agent

    # ========================================================
    # 6. SCHEDULING
    # ========================================================

    def create_schedule(
        self,
        agent: Agent,
        delay_seconds: int = 5,
    ) -> AgentSchedule:

        scheduled_time = datetime.now()

        schedule = AgentSchedule(
            schedule_id=str(uuid.uuid4()),
            agent_id=agent.agent_id,
            agent_name=agent.agent_name,
            scheduled_time=scheduled_time,
        )

        self.schedules[schedule.schedule_id] = schedule

        logger.info(
            "Schedule created | agent=%s | schedule_id=%s | delay=%ss",
            agent.agent_name,
            schedule.schedule_id,
            delay_seconds,
        )

        self.record_event(
            EventType.SCHEDULE_CREATED,
            agent,
            EventStatus.SUCCESS,
            "Agent schedule created",
            {
                "delay_seconds": delay_seconds,
                "scheduled_time": scheduled_time.isoformat(),
            },
            schedule_id=schedule.schedule_id,
        )

        return schedule

    # ========================================================
    # 7. EXECUTION CONTROL
    # ========================================================

    def create_execution(
        self,
        agent: Agent,
        request: str,
    ) -> AgentExecution:

        execution = AgentExecution(
            execution_id=str(uuid.uuid4()),
            agent_id=agent.agent_id,
            agent_name=agent.agent_name,
            request=request,
        )

        self.executions[execution.execution_id] = execution

        logger.info(
            "Execution created | agent=%s | execution_id=%s",
            agent.agent_name,
            execution.execution_id,
        )

        return execution

    def execute_agent(
        self,
        execution: AgentExecution,
    ) -> bool:

        agent = self.agents.get(execution.agent_id)

        if not agent:
            logger.error("Execution failed: agent not found")
            return False

        execution.status = ExecutionStatus.RUNNING
        execution.started_at = datetime.now()

        self.record_event(
            EventType.EXECUTION_STARTED,
            agent,
            EventStatus.SUCCESS,
            "Agent execution started",
            execution_id=execution.execution_id,
        )

        logger.info(
            "Agent execution started | agent=%s | execution_id=%s",
            agent.agent_name,
            execution.execution_id,
        )

        try:
            # Simulated agent processing
            time.sleep(1)

            execution.response = (
                "Agriculture request processed successfully by "
                f"{agent.agent_name}."
            )

            execution.status = ExecutionStatus.COMPLETED
            execution.completed_at = datetime.now()

            health = self.health.get(agent.agent_id)

            if health:
                health.successful_executions += 1
                health.response_time_ms = 1000

            self.record_event(
                EventType.EXECUTION_COMPLETED,
                agent,
                EventStatus.SUCCESS,
                "Agent execution completed successfully",
                {
                    "response_length": len(execution.response),
                },
                execution_id=execution.execution_id,
            )

            logger.info(
                "Agent execution completed | agent=%s | execution_id=%s",
                agent.agent_name,
                execution.execution_id,
            )

            return True

        except Exception as exc:

            execution.status = ExecutionStatus.FAILED
            execution.error = str(exc)
            execution.completed_at = datetime.now()

            health = self.health.get(agent.agent_id)

            if health:
                health.failed_executions += 1
                health.error_count += 1

            self.record_event(
                EventType.EXECUTION_FAILED,
                agent,
                EventStatus.FAILED,
                "Agent execution failed",
                {"error": str(exc)},
                execution_id=execution.execution_id,
            )

            logger.exception(
                "Agent execution failed | agent=%s",
                agent.agent_name,
            )

            return False

    # ========================================================
    # 8. HEALTH MANAGEMENT
    # ========================================================

    def register_health(self, agent: Agent) -> AgentHealth:

        health = AgentHealth(
            health_id=str(uuid.uuid4()),
            agent_id=agent.agent_id,
            agent_name=agent.agent_name,
        )

        self.health[agent.agent_id] = health

        logger.info(
            "Health monitoring registered | agent=%s",
            agent.agent_name,
        )

        return health

    def health_check(self, agent: Agent) -> HealthStatus:

        health = self.health.get(agent.agent_id)

        if not health:
            logger.warning(
                "Health record not found | agent=%s",
                agent.agent_name,
            )
            return HealthStatus.UNKNOWN

        health.last_heartbeat = datetime.now()

        if agent.status != AgentStatus.ACTIVE:
            health.status = HealthStatus.UNHEALTHY

        elif health.failed_executions >= 3:
            health.status = HealthStatus.UNHEALTHY

        elif health.error_count >= 1:
            health.status = HealthStatus.DEGRADED

        else:
            health.status = HealthStatus.HEALTHY

        self.record_event(
            EventType.HEALTH_CHECK,
            agent,
            EventStatus.SUCCESS,
            "Agent health check completed",
            {
                "health_status": health.status.value,
                "successful_executions": health.successful_executions,
                "failed_executions": health.failed_executions,
            },
        )

        logger.info(
            "Health check completed | agent=%s | status=%s",
            agent.agent_name,
            health.status.value,
        )

        return health.status

    # ========================================================
    # DISPLAY CONTROL PLANE
    # ========================================================

    def display_summary(self):

        print("\n")
        print("=" * 75)
        print("END-TO-END CONTROL PLANE SUMMARY")
        print("=" * 75)

        print(f"Registered Agents : {len(self.agents)}")
        print(f"Configurations    : {len(self.configurations)}")
        print(f"Permissions       : {len(self.permissions)}")
        print(f"Routing Rules     : {len(self.routing_rules)}")
        print(f"Schedules         : {len(self.schedules)}")
        print(f"Executions        : {len(self.executions)}")
        print(f"Health Records    : {len(self.health)}")
        print(f"Control Events    : {len(self.events)}")

        print("=" * 75)

        print("\nAGENTS")

        for agent in self.agents.values():
            print("-" * 75)
            print(f"Agent Name    : {agent.agent_name}")
            print(f"Agent ID      : {agent.agent_id}")
            print(f"Model         : {agent.model}")
            print(f"Version       : {agent.version}")
            print(f"Environment   : {agent.environment.value}")
            print(f"Status        : {agent.status.value}")
            print(f"Capabilities  : {', '.join(agent.capabilities)}")

        print("\nCONFIGURATIONS")

        for configuration in self.configurations.values():
            print("-" * 75)
            print(f"Config ID     : {configuration.config_id}")
            print(f"Model         : {configuration.model}")
            print(f"Temperature   : {configuration.temperature}")
            print(f"Max Tokens    : {configuration.max_tokens}")
            print(f"Language      : {configuration.language}")
            print(f"Tools         : {configuration.tools}")
            print(f"Environment   : {configuration.environment.value}")
            print(f"Enabled       : {configuration.enabled}")

        print("\nHEALTH")

        for health in self.health.values():
            print("-" * 75)
            print(f"Agent         : {health.agent_name}")
            print(f"Health Status : {health.status.value}")
            print(f"Successful    : {health.successful_executions}")
            print(f"Failed        : {health.failed_executions}")
            print(f"Errors        : {health.error_count}")

        print("\nEXECUTIONS")

        for execution in self.executions.values():
            print("-" * 75)
            print(f"Execution ID  : {execution.execution_id}")
            print(f"Agent         : {execution.agent_name}")
            print(f"Request       : {execution.request}")
            print(f"Status        : {execution.status.value}")
            print(f"Response      : {execution.response}")
            print(f"Error         : {execution.error}")

        print("\nCONTROL EVENTS")

        for event in self.events:
            print("-" * 75)
            print(f"Type          : {event.event_type.value}")
            print(f"Agent         : {event.agent_name}")
            print(f"Status        : {event.status.value}")
            print(f"Message       : {event.message}")

        print("=" * 75)


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info("Starting Exercise 122 - End-to-End Control Plane")

    control_plane = EndToEndControlPlane()

    # --------------------------------------------------------
    # STEP 1: REGISTER AGENT
    # --------------------------------------------------------

    agent = control_plane.register_agent(
        agent_name="AgriAssistant",
        description="AI assistant for agriculture-related questions",
        model="llama3.2",
        capabilities=[
            "question_answering",
            "agriculture_information",
            "data_analysis",
        ],
        owner="GramSwaram AI Team",
        environment=Environment.DEVELOPMENT,
    )

    # --------------------------------------------------------
    # STEP 2: ACTIVATE AGENT
    # --------------------------------------------------------

    control_plane.activate_agent(agent.agent_id)

    # --------------------------------------------------------
    # STEP 3: CREATE CONFIGURATION
    # --------------------------------------------------------

    control_plane.create_configuration(
        agent=agent,
        temperature=0.3,
        max_tokens=2000,
        tools=[
            "web_search",
            "calculator",
            "data_analysis",
        ],
        language="English",
    )

    # --------------------------------------------------------
    # STEP 4: GRANT PERMISSIONS
    # --------------------------------------------------------

    control_plane.grant_permission(
        agent,
        PermissionAction.AGRICULTURE_INFO,
    )

    control_plane.grant_permission(
        agent,
        PermissionAction.DATA_ANALYSIS,
    )

    control_plane.grant_permission(
        agent,
        PermissionAction.WEB_SEARCH,
    )

    # --------------------------------------------------------
    # STEP 5: CREATE ROUTING RULE
    # --------------------------------------------------------

    control_plane.add_routing_rule(
        RequestType.AGRICULTURE,
        agent,
        priority=1,
    )

    # --------------------------------------------------------
    # STEP 6: REGISTER HEALTH MONITORING
    # --------------------------------------------------------

    control_plane.register_health(agent)

    # --------------------------------------------------------
    # STEP 7: CREATE SCHEDULE
    # --------------------------------------------------------

    schedule = control_plane.create_schedule(
        agent,
        delay_seconds=5,
    )

    # --------------------------------------------------------
    # STEP 8: HEALTH CHECK BEFORE EXECUTION
    # --------------------------------------------------------

    control_plane.health_check(agent)

    # --------------------------------------------------------
    # STEP 9: ROUTE REQUEST
    # --------------------------------------------------------

    routed_agent = control_plane.route_request(
        RequestType.AGRICULTURE
    )

    # --------------------------------------------------------
    # STEP 10: EXECUTE REQUEST
    # --------------------------------------------------------

    if routed_agent:

        execution = control_plane.create_execution(
            routed_agent,
            "Provide basic information about improving crop production.",
        )

        control_plane.execute_agent(execution)

        schedule.execution_count += 1

    # --------------------------------------------------------
    # STEP 11: HEALTH CHECK AFTER EXECUTION
    # --------------------------------------------------------

    control_plane.health_check(agent)

    # --------------------------------------------------------
    # STEP 12: DISPLAY COMPLETE CONTROL PLANE
    # --------------------------------------------------------

    control_plane.display_summary()

    # --------------------------------------------------------
    # FINAL RESULT
    # --------------------------------------------------------

    logger.info(
        "Exercise 122 - End-to-End Control Plane completed successfully"
    )


if __name__ == "__main__":
    main()