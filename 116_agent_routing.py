import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional
from uuid import uuid4


# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agent_routing")


# ---------------------------------------------------------
# Agent Status
# ---------------------------------------------------------

class AgentStatus(Enum):
    REGISTERED = "registered"
    ACTIVE = "active"
    INACTIVE = "inactive"


# ---------------------------------------------------------
# Request Type
# ---------------------------------------------------------

class RequestType(Enum):
    AGRICULTURE = "agriculture"
    CUSTOMER_SUPPORT = "customer_support"
    GENERAL = "general"


# ---------------------------------------------------------
# Registered Agent
# ---------------------------------------------------------

@dataclass
class RegisteredAgent:
    agent_id: str
    agent_name: str
    capabilities: List[str]
    status: AgentStatus = AgentStatus.REGISTERED


# ---------------------------------------------------------
# Routing Rule
# ---------------------------------------------------------

@dataclass
class RoutingRule:
    request_type: RequestType
    agent_id: str
    priority: int = 1
    enabled: bool = True


# ---------------------------------------------------------
# Routing Result
# ---------------------------------------------------------

@dataclass
class RoutingResult:
    request_id: str
    request_type: RequestType
    agent_id: Optional[str]
    agent_name: Optional[str]
    matched_rule: Optional[str]
    status: str


# ---------------------------------------------------------
# Agent Router
# ---------------------------------------------------------

class AgentRouter:

    def __init__(self):
        self.agents: Dict[str, RegisteredAgent] = {}
        self.rules: List[RoutingRule] = []

        logger.info("Agent Router initialized")

    # -----------------------------------------------------
    # Register Agent
    # -----------------------------------------------------

    def register_agent(
        self,
        agent_name: str,
        capabilities: List[str],
    ) -> RegisteredAgent:

        agent = RegisteredAgent(
            agent_id=str(uuid4()),
            agent_name=agent_name,
            capabilities=capabilities,
            status=AgentStatus.ACTIVE,
        )

        self.agents[agent.agent_id] = agent

        logger.info(
            "Agent registered | name=%s | agent_id=%s | status=%s",
            agent.agent_name,
            agent.agent_id,
            agent.status.value,
        )

        return agent

    # -----------------------------------------------------
    # Add Routing Rule
    # -----------------------------------------------------

    def add_routing_rule(
        self,
        request_type: RequestType,
        agent_id: str,
        priority: int = 1,
    ) -> Optional[RoutingRule]:

        if agent_id not in self.agents:
            logger.warning(
                "Cannot create routing rule. Agent not found: %s",
                agent_id,
            )
            return None

        rule = RoutingRule(
            request_type=request_type,
            agent_id=agent_id,
            priority=priority,
        )

        self.rules.append(rule)

        # Lower priority number means higher priority.
        self.rules.sort(key=lambda item: item.priority)

        logger.info(
            "Routing rule added | request_type=%s | agent_id=%s | priority=%s",
            request_type.value,
            agent_id,
            priority,
        )

        return rule

    # -----------------------------------------------------
    # Route Request
    # -----------------------------------------------------

    def route_request(
        self,
        request_type: RequestType,
    ) -> RoutingResult:

        request_id = str(uuid4())

        logger.info(
            "Routing request | request_id=%s | request_type=%s",
            request_id,
            request_type.value,
        )

        matching_rules = [
            rule
            for rule in self.rules
            if rule.request_type == request_type
            and rule.enabled
        ]

        for rule in matching_rules:

            agent = self.agents.get(rule.agent_id)

            if not agent:
                logger.warning(
                    "Routing rule points to missing agent | agent_id=%s",
                    rule.agent_id,
                )
                continue

            if agent.status != AgentStatus.ACTIVE:
                logger.warning(
                    "Agent is not active | agent=%s | status=%s",
                    agent.agent_name,
                    agent.status.value,
                )
                continue

            logger.info(
                "Request routed successfully | request_id=%s | agent=%s",
                request_id,
                agent.agent_name,
            )

            return RoutingResult(
                request_id=request_id,
                request_type=request_type,
                agent_id=agent.agent_id,
                agent_name=agent.agent_name,
                matched_rule=f"{request_type.value} -> {agent.agent_name}",
                status="ROUTED",
            )

        logger.warning(
            "No active routing rule found | request_id=%s | request_type=%s",
            request_id,
            request_type.value,
        )

        return RoutingResult(
            request_id=request_id,
            request_type=request_type,
            agent_id=None,
            agent_name=None,
            matched_rule=None,
            status="NO_ROUTE",
        )

    # -----------------------------------------------------
    # Display Routing Rules
    # -----------------------------------------------------

    def display_rules(self) -> None:

        print("\n" + "=" * 70)
        print("AGENT ROUTING RULES")
        print("=" * 70)

        if not self.rules:
            print("No routing rules configured.")
            print("=" * 70)
            return

        for index, rule in enumerate(self.rules, start=1):

            agent = self.agents.get(rule.agent_id)

            agent_name = (
                agent.agent_name
                if agent
                else "Unknown Agent"
            )

            print(
                f"{index}. "
                f"{rule.request_type.value} "
                f"-> {agent_name} "
                f"| Priority: {rule.priority} "
                f"| Enabled: {rule.enabled}"
            )

        print("=" * 70)

    # -----------------------------------------------------
    # Display Agents
    # -----------------------------------------------------

    def display_agents(self) -> None:

        print("\n" + "=" * 70)
        print("REGISTERED AGENTS")
        print("=" * 70)

        for agent in self.agents.values():

            print(
                f"Agent: {agent.agent_name} | "
                f"ID: {agent.agent_id} | "
                f"Status: {agent.status.value} | "
                f"Capabilities: {agent.capabilities}"
            )

        print("=" * 70)

    # -----------------------------------------------------
    # Display Routing Result
    # -----------------------------------------------------

    @staticmethod
    def display_routing_result(
        result: RoutingResult,
    ) -> None:

        print("\n" + "-" * 70)
        print("ROUTING RESULT")
        print("-" * 70)

        print(f"Request ID     : {result.request_id}")
        print(f"Request Type   : {result.request_type.value}")
        print(f"Agent ID       : {result.agent_id}")
        print(f"Agent Name     : {result.agent_name}")
        print(f"Matched Rule   : {result.matched_rule}")
        print(f"Status         : {result.status}")

        print("-" * 70)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    logger.info("Starting Exercise 116 - Agent Routing")

    router = AgentRouter()

    # -----------------------------------------------------
    # Register Agents
    # -----------------------------------------------------

    agri_agent = router.register_agent(
        agent_name="AgriAssistant",
        capabilities=[
            "agriculture",
            "farming",
            "crop_information",
        ],
    )

    support_agent = router.register_agent(
        agent_name="CustomerSupportAgent",
        capabilities=[
            "customer_support",
            "issue_resolution",
            "general_support",
        ],
    )

    general_agent = router.register_agent(
        agent_name="GeneralAssistant",
        capabilities=[
            "general",
            "question_answering",
        ],
    )

    # -----------------------------------------------------
    # Display Registered Agents
    # -----------------------------------------------------

    router.display_agents()

    # -----------------------------------------------------
    # Configure Routing Rules
    # -----------------------------------------------------

    router.add_routing_rule(
        request_type=RequestType.AGRICULTURE,
        agent_id=agri_agent.agent_id,
        priority=1,
    )

    router.add_routing_rule(
        request_type=RequestType.CUSTOMER_SUPPORT,
        agent_id=support_agent.agent_id,
        priority=1,
    )

    router.add_routing_rule(
        request_type=RequestType.GENERAL,
        agent_id=general_agent.agent_id,
        priority=1,
    )

    # -----------------------------------------------------
    # Display Routing Rules
    # -----------------------------------------------------

    router.display_rules()

    # -----------------------------------------------------
    # Test Agriculture Request
    # -----------------------------------------------------

    logger.info("Testing agriculture request")

    agriculture_result = router.route_request(
        RequestType.AGRICULTURE
    )

    router.display_routing_result(
        agriculture_result
    )

    # -----------------------------------------------------
    # Test Customer Support Request
    # -----------------------------------------------------

    logger.info("Testing customer support request")

    support_result = router.route_request(
        RequestType.CUSTOMER_SUPPORT
    )

    router.display_routing_result(
        support_result
    )

    # -----------------------------------------------------
    # Test General Request
    # -----------------------------------------------------

    logger.info("Testing general request")

    general_result = router.route_request(
        RequestType.GENERAL
    )

    router.display_routing_result(
        general_result
    )

    # -----------------------------------------------------
    # Test Unknown Routing
    # -----------------------------------------------------

    logger.info("Testing request type without routing rule")

    # Temporarily disable the general rule
    for rule in router.rules:

        if rule.request_type == RequestType.GENERAL:
            rule.enabled = False

    no_route_result = router.route_request(
        RequestType.GENERAL
    )

    router.display_routing_result(
        no_route_result
    )

    logger.info(
        "Exercise 116 - Agent Routing completed successfully"
    )


if __name__ == "__main__":
    main()