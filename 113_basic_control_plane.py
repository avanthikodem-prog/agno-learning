import logging
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Optional


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("basic_control_plane")


# ============================================================
# AGENT STATUS
# ============================================================

class AgentStatus(Enum):
    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


# ============================================================
# AGENT INFORMATION
# ============================================================

@dataclass
class AgentInfo:
    agent_id: str
    agent_name: str
    description: str
    model: str
    status: AgentStatus = AgentStatus.REGISTERED
    created_at: float = field(
        default_factory=lambda: __import__("time").time()
    )


# ============================================================
# CONTROL PLANE
# ============================================================

class ControlPlane:

    def __init__(self):

        self.agents: Dict[str, AgentInfo] = {}

        logger.info(
            "Control Plane initialized"
        )


    # ========================================================
    # REGISTER AGENT
    # ========================================================

    def register_agent(
        self,
        agent_name: str,
        description: str,
        model: str,
    ) -> AgentInfo:

        agent_id = str(uuid.uuid4())

        agent = AgentInfo(
            agent_id=agent_id,
            agent_name=agent_name,
            description=description,
            model=model,
        )

        self.agents[agent_id] = agent

        logger.info(
            "Agent registered | agent_id=%s | name=%s | model=%s",
            agent_id,
            agent_name,
            model,
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
                "Cannot activate agent | agent_id=%s | reason=not_found",
                agent_id,
            )

            return False

        agent.status = AgentStatus.ACTIVE

        logger.info(
            "Agent activated | agent_id=%s | name=%s",
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
                "Cannot deactivate agent | agent_id=%s | reason=not_found",
                agent_id,
            )

            return False

        agent.status = AgentStatus.INACTIVE

        logger.info(
            "Agent deactivated | agent_id=%s | name=%s",
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
    ) -> Optional[AgentInfo]:

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
    # LIST AGENTS
    # ========================================================

    def list_agents(self):

        logger.info(
            "Listing registered agents | count=%s",
            len(self.agents),
        )

        return list(self.agents.values())


    # ========================================================
    # DISPLAY CONTROL PLANE
    # ========================================================

    def display_agents(self):

        print("\n" + "=" * 70)
        print("CONTROL PLANE - REGISTERED AGENTS")
        print("=" * 70)

        if not self.agents:

            print("No agents registered.")

            return

        for index, agent in enumerate(
            self.agents.values(),
            start=1,
        ):

            print(f"\nAgent {index}")
            print("-" * 70)

            print(
                f"Agent ID   : {agent.agent_id}"
            )

            print(
                f"Name       : {agent.agent_name}"
            )

            print(
                f"Description: {agent.description}"
            )

            print(
                f"Model      : {agent.model}"
            )

            print(
                f"Status     : {agent.status.value}"
            )

        print("=" * 70)


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info(
        "Starting Exercise 113 - Basic Control Plane"
    )

    # --------------------------------------------------------
    # Create Control Plane
    # --------------------------------------------------------

    control_plane = ControlPlane()

    # --------------------------------------------------------
    # Register Agent
    # --------------------------------------------------------

    agent = control_plane.register_agent(
        agent_name="AgriAssistant",
        description="AI assistant for agriculture-related questions",
        model="llama3.2",
    )

    print("\nAgent registered successfully.")

    # --------------------------------------------------------
    # Display initial status
    # --------------------------------------------------------

    print(
        f"Initial status: {agent.status.value}"
    )

    # --------------------------------------------------------
    # Activate Agent
    # --------------------------------------------------------

    control_plane.activate_agent(
        agent.agent_id
    )

    # --------------------------------------------------------
    # Check Agent
    # --------------------------------------------------------

    registered_agent = control_plane.get_agent(
        agent.agent_id
    )

    if registered_agent:

        print(
            f"Current status: "
            f"{registered_agent.status.value}"
        )

    # --------------------------------------------------------
    # Display all agents
    # --------------------------------------------------------

    control_plane.display_agents()

    # --------------------------------------------------------
    # Deactivate Agent
    # --------------------------------------------------------

    control_plane.deactivate_agent(
        agent.agent_id
    )

    # --------------------------------------------------------
    # Check final status
    # --------------------------------------------------------

    final_agent = control_plane.get_agent(
        agent.agent_id
    )

    if final_agent:

        print(
            f"\nFinal status: "
            f"{final_agent.status.value}"
        )

    # --------------------------------------------------------
    # Final Agent List
    # --------------------------------------------------------

    agents = control_plane.list_agents()

    print(
        f"Total registered agents: {len(agents)}"
    )

    logger.info(
        "Exercise 113 completed successfully"
    )


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()