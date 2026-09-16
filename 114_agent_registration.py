import logging
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agent_registration")


# ============================================================
# AGENT STATUS
# ============================================================

class AgentStatus(Enum):
    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


# ============================================================
# AGENT REGISTRATION DATA
# ============================================================

@dataclass
class AgentRegistration:
    agent_id: str
    agent_name: str
    description: str
    model: str
    version: str
    capabilities: List[str]
    owner: str
    environment: str

    status: AgentStatus = AgentStatus.REGISTERED

    registered_at: float = field(
        default_factory=time.time
    )


# ============================================================
# AGENT REGISTRY
# ============================================================

class AgentRegistry:

    def __init__(self):

        self.agents: Dict[str, AgentRegistration] = {}

        logger.info(
            "Agent Registry initialized"
        )


    # ========================================================
    # REGISTER AGENT
    # ========================================================

    def register_agent(
        self,
        agent_name: str,
        description: str,
        model: str,
        version: str,
        capabilities: List[str],
        owner: str,
        environment: str,
    ) -> Optional[AgentRegistration]:

        # ----------------------------------------------------
        # Check duplicate agent name
        # ----------------------------------------------------

        for existing_agent in self.agents.values():

            if existing_agent.agent_name.lower() == agent_name.lower():

                logger.error(
                    "Agent registration failed | "
                    "name=%s | reason=duplicate_name",
                    agent_name,
                )

                return None

        # ----------------------------------------------------
        # Generate unique agent ID
        # ----------------------------------------------------

        agent_id = str(uuid.uuid4())

        # ----------------------------------------------------
        # Create registration
        # ----------------------------------------------------

        agent = AgentRegistration(
            agent_id=agent_id,
            agent_name=agent_name,
            description=description,
            model=model,
            version=version,
            capabilities=capabilities,
            owner=owner,
            environment=environment,
        )

        # ----------------------------------------------------
        # Store agent
        # ----------------------------------------------------

        self.agents[agent_id] = agent

        logger.info(
            "Agent registered | "
            "agent_id=%s | "
            "name=%s | "
            "version=%s | "
            "environment=%s",
            agent_id,
            agent_name,
            version,
            environment,
        )

        return agent


    # ========================================================
    # ACTIVATE AGENT
    # ========================================================

    def activate_agent(
        self,
        agent_id: str,
    ) -> bool:

        agent = self.agents.get(agent_id)

        if agent is None:

            logger.error(
                "Activation failed | "
                "agent_id=%s | reason=not_found",
                agent_id,
            )

            return False

        agent.status = AgentStatus.ACTIVE

        logger.info(
            "Agent activated | "
            "agent_id=%s | name=%s",
            agent_id,
            agent.agent_name,
        )

        return True


    # ========================================================
    # DEACTIVATE AGENT
    # ========================================================

    def deactivate_agent(
        self,
        agent_id: str,
    ) -> bool:

        agent = self.agents.get(agent_id)

        if agent is None:

            logger.error(
                "Deactivation failed | "
                "agent_id=%s | reason=not_found",
                agent_id,
            )

            return False

        agent.status = AgentStatus.INACTIVE

        logger.info(
            "Agent deactivated | "
            "agent_id=%s | name=%s",
            agent_id,
            agent.agent_name,
        )

        return True


    # ========================================================
    # GET AGENT
    # ========================================================

    def get_agent(
        self,
        agent_id: str,
    ) -> Optional[AgentRegistration]:

        agent = self.agents.get(agent_id)

        if agent:

            logger.info(
                "Agent retrieved | agent_id=%s",
                agent_id,
            )

        else:

            logger.warning(
                "Agent not found | agent_id=%s",
                agent_id,
            )

        return agent


    # ========================================================
    # FIND AGENT BY NAME
    # ========================================================

    def find_by_name(
        self,
        agent_name: str,
    ) -> Optional[AgentRegistration]:

        for agent in self.agents.values():

            if agent.agent_name.lower() == agent_name.lower():

                logger.info(
                    "Agent found by name | name=%s | agent_id=%s",
                    agent_name,
                    agent.agent_id,
                )

                return agent

        logger.warning(
            "Agent not found by name | name=%s",
            agent_name,
        )

        return None


    # ========================================================
    # LIST AGENTS
    # ========================================================

    def list_agents(self) -> List[AgentRegistration]:

        logger.info(
            "Listing agents | count=%s",
            len(self.agents),
        )

        return list(self.agents.values())


    # ========================================================
    # DISPLAY AGENT
    # ========================================================

    def display_agent(
        self,
        agent: AgentRegistration,
    ):

        print("\n" + "-" * 70)

        print(
            f"Agent ID      : {agent.agent_id}"
        )

        print(
            f"Agent Name    : {agent.agent_name}"
        )

        print(
            f"Description   : {agent.description}"
        )

        print(
            f"Model         : {agent.model}"
        )

        print(
            f"Version       : {agent.version}"
        )

        print(
            f"Owner         : {agent.owner}"
        )

        print(
            f"Environment   : {agent.environment}"
        )

        print(
            f"Status        : {agent.status.value}"
        )

        print(
            f"Capabilities  : {', '.join(agent.capabilities)}"
        )

        print("-" * 70)


    # ========================================================
    # DISPLAY REGISTRY
    # ========================================================

    def display_registry(self):

        print("\n" + "=" * 70)
        print("AGENT REGISTRY")
        print("=" * 70)

        if not self.agents:

            print("No agents registered.")

            return

        for index, agent in enumerate(
            self.agents.values(),
            start=1,
        ):

            print(f"\nAgent {index}")

            self.display_agent(agent)

        print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info(
        "Starting Exercise 114 - Agent Registration"
    )

    # --------------------------------------------------------
    # Create Registry
    # --------------------------------------------------------

    registry = AgentRegistry()

    # --------------------------------------------------------
    # Register first agent
    # --------------------------------------------------------

    agri_agent = registry.register_agent(
        agent_name="AgriAssistant",
        description=(
            "AI assistant for agriculture-related "
            "questions and farmer services"
        ),
        model="llama3.2",
        version="1.0.0",
        capabilities=[
            "question_answering",
            "agriculture_information",
            "data_analysis",
        ],
        owner="GramSwaram AI Team",
        environment="development",
    )

    if agri_agent:

        print("\nAgriAssistant registered successfully.")

        registry.display_agent(
            agri_agent
        )

    # --------------------------------------------------------
    # Register second agent
    # --------------------------------------------------------

    support_agent = registry.register_agent(
        agent_name="CustomerSupportAgent",
        description=(
            "AI assistant for customer support "
            "and service requests"
        ),
        model="llama3.2",
        version="1.0.0",
        capabilities=[
            "question_answering",
            "customer_support",
            "issue_resolution",
        ],
        owner="GramSwaram AI Team",
        environment="development",
    )

    if support_agent:

        print(
            "\nCustomerSupportAgent "
            "registered successfully."
        )

    # --------------------------------------------------------
    # Attempt duplicate registration
    # --------------------------------------------------------

    duplicate_agent = registry.register_agent(
        agent_name="AgriAssistant",
        description="Duplicate agent test",
        model="llama3.2",
        version="1.0.1",
        capabilities=[
            "testing",
        ],
        owner="Test Team",
        environment="development",
    )

    if duplicate_agent is None:

        print(
            "\nDuplicate registration rejected successfully."
        )

    # --------------------------------------------------------
    # Activate agents
    # --------------------------------------------------------

    if agri_agent:

        registry.activate_agent(
            agri_agent.agent_id
        )

    if support_agent:

        registry.activate_agent(
            support_agent.agent_id
        )

    # --------------------------------------------------------
    # Find agent by name
    # --------------------------------------------------------

    found_agent = registry.find_by_name(
        "AgriAssistant"
    )

    if found_agent:

        print(
            "\nAgent search successful:"
        )

        print(
            f"Found: {found_agent.agent_name}"
        )

        print(
            f"Version: {found_agent.version}"
        )

    # --------------------------------------------------------
    # Display all agents
    # --------------------------------------------------------

    registry.display_registry()

    # --------------------------------------------------------
    # Deactivate one agent
    # --------------------------------------------------------

    if support_agent:

        registry.deactivate_agent(
            support_agent.agent_id
        )

    # --------------------------------------------------------
    # Display final registry
    # --------------------------------------------------------

    print("\nFinal Registry State:")

    registry.display_registry()

    # --------------------------------------------------------
    # Count agents
    # --------------------------------------------------------

    agents = registry.list_agents()

    print(
        f"\nTotal registered agents: {len(agents)}"
    )

    logger.info(
        "Exercise 114 completed successfully"
    )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()