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

logger = logging.getLogger("agent_permissions")


# ---------------------------------------------------------
# Agent Status
# ---------------------------------------------------------

class AgentStatus(Enum):
    REGISTERED = "registered"
    ACTIVE = "active"
    INACTIVE = "inactive"


# ---------------------------------------------------------
# Permission Actions
# ---------------------------------------------------------

class PermissionAction(Enum):
    WEB_SEARCH = "web_search"
    DATA_ANALYSIS = "data_analysis"
    CUSTOMER_SUPPORT = "customer_support"
    AGRICULTURE_INFO = "agriculture_info"
    ISSUE_RESOLUTION = "issue_resolution"
    DELETE_USER_DATA = "delete_user_data"
    SYSTEM_CONFIGURATION = "system_configuration"


# ---------------------------------------------------------
# Permission Effect
# ---------------------------------------------------------

class PermissionEffect(Enum):
    ALLOW = "allow"
    DENY = "deny"


# ---------------------------------------------------------
# Registered Agent
# ---------------------------------------------------------

@dataclass
class RegisteredAgent:
    agent_id: str
    agent_name: str
    status: AgentStatus = AgentStatus.ACTIVE


# ---------------------------------------------------------
# Agent Permission
# ---------------------------------------------------------

@dataclass
class AgentPermission:
    permission_id: str
    agent_id: str
    action: PermissionAction
    effect: PermissionEffect
    granted_by: str
    enabled: bool = True


# ---------------------------------------------------------
# Permission Check Result
# ---------------------------------------------------------

@dataclass
class PermissionCheckResult:
    request_id: str
    agent_id: str
    agent_name: str
    action: PermissionAction
    allowed: bool
    reason: str


# ---------------------------------------------------------
# Permission Manager
# ---------------------------------------------------------

class PermissionManager:

    def __init__(self):
        self.agents: Dict[str, RegisteredAgent] = {}
        self.permissions: Dict[str, List[AgentPermission]] = {}

        logger.info("Permission Manager initialized")

    # -----------------------------------------------------
    # Register Agent
    # -----------------------------------------------------

    def register_agent(
        self,
        agent_name: str,
    ) -> RegisteredAgent:

        agent = RegisteredAgent(
            agent_id=str(uuid4()),
            agent_name=agent_name,
            status=AgentStatus.ACTIVE,
        )

        self.agents[agent.agent_id] = agent
        self.permissions[agent.agent_id] = []

        logger.info(
            "Agent registered | name=%s | agent_id=%s | status=%s",
            agent.agent_name,
            agent.agent_id,
            agent.status.value,
        )

        return agent

    # -----------------------------------------------------
    # Grant Permission
    # -----------------------------------------------------

    def grant_permission(
        self,
        agent_id: str,
        action: PermissionAction,
        granted_by: str,
    ) -> Optional[AgentPermission]:

        agent = self.agents.get(agent_id)

        if not agent:
            logger.warning(
                "Cannot grant permission. Agent not found: %s",
                agent_id,
            )
            return None

        permission = AgentPermission(
            permission_id=str(uuid4()),
            agent_id=agent_id,
            action=action,
            effect=PermissionEffect.ALLOW,
            granted_by=granted_by,
            enabled=True,
        )

        self.permissions[agent_id].append(permission)

        logger.info(
            "Permission granted | agent=%s | action=%s | granted_by=%s",
            agent.agent_name,
            action.value,
            granted_by,
        )

        return permission

    # -----------------------------------------------------
    # Deny Permission
    # -----------------------------------------------------

    def deny_permission(
        self,
        agent_id: str,
        action: PermissionAction,
        granted_by: str,
    ) -> Optional[AgentPermission]:

        agent = self.agents.get(agent_id)

        if not agent:
            logger.warning(
                "Cannot deny permission. Agent not found: %s",
                agent_id,
            )
            return None

        permission = AgentPermission(
            permission_id=str(uuid4()),
            agent_id=agent_id,
            action=action,
            effect=PermissionEffect.DENY,
            granted_by=granted_by,
            enabled=True,
        )

        self.permissions[agent_id].append(permission)

        logger.info(
            "Permission denied | agent=%s | action=%s | granted_by=%s",
            agent.agent_name,
            action.value,
            granted_by,
        )

        return permission

    # -----------------------------------------------------
    # Check Permission
    # -----------------------------------------------------

    def check_permission(
        self,
        agent_id: str,
        action: PermissionAction,
    ) -> PermissionCheckResult:

        request_id = str(uuid4())

        agent = self.agents.get(agent_id)

        if not agent:

            logger.warning(
                "Permission check failed. Agent not found | agent_id=%s",
                agent_id,
            )

            return PermissionCheckResult(
                request_id=request_id,
                agent_id=agent_id,
                agent_name="Unknown",
                action=action,
                allowed=False,
                reason="Agent not found",
            )

        if agent.status != AgentStatus.ACTIVE:

            logger.warning(
                "Permission denied because agent is inactive | agent=%s",
                agent.agent_name,
            )

            return PermissionCheckResult(
                request_id=request_id,
                agent_id=agent_id,
                agent_name=agent.agent_name,
                action=action,
                allowed=False,
                reason="Agent is inactive",
            )

        agent_permissions = self.permissions.get(
            agent_id,
            [],
        )

        # Find the latest enabled permission for this action.
        matching_permissions = [
            permission
            for permission in agent_permissions
            if permission.action == action
            and permission.enabled
        ]

        if not matching_permissions:

            logger.warning(
                "Permission denied | agent=%s | action=%s | reason=no permission",
                agent.agent_name,
                action.value,
            )

            return PermissionCheckResult(
                request_id=request_id,
                agent_id=agent_id,
                agent_name=agent.agent_name,
                action=action,
                allowed=False,
                reason="No permission configured",
            )

        latest_permission = matching_permissions[-1]

        if latest_permission.effect == PermissionEffect.ALLOW:

            logger.info(
                "Permission allowed | agent=%s | action=%s",
                agent.agent_name,
                action.value,
            )

            return PermissionCheckResult(
                request_id=request_id,
                agent_id=agent_id,
                agent_name=agent.agent_name,
                action=action,
                allowed=True,
                reason="Permission explicitly allowed",
            )

        logger.warning(
            "Permission denied | agent=%s | action=%s | reason=explicit deny",
            agent.agent_name,
            action.value,
        )

        return PermissionCheckResult(
            request_id=request_id,
            agent_id=agent_id,
            agent_name=agent.agent_name,
            action=action,
            allowed=False,
            reason="Permission explicitly denied",
        )

    # -----------------------------------------------------
    # Disable Permission
    # -----------------------------------------------------

    def disable_permission(
        self,
        agent_id: str,
        action: PermissionAction,
    ) -> bool:

        agent_permissions = self.permissions.get(
            agent_id,
            [],
        )

        for permission in reversed(agent_permissions):

            if (
                permission.action == action
                and permission.enabled
            ):

                permission.enabled = False

                logger.info(
                    "Permission disabled | agent_id=%s | action=%s",
                    agent_id,
                    action.value,
                )

                return True

        logger.warning(
            "No active permission found to disable | agent_id=%s | action=%s",
            agent_id,
            action.value,
        )

        return False

    # -----------------------------------------------------
    # Display Permissions
    # -----------------------------------------------------

    def display_permissions(
        self,
        agent_id: str,
    ) -> None:

        agent = self.agents.get(agent_id)

        if not agent:
            logger.warning(
                "Cannot display permissions. Agent not found: %s",
                agent_id,
            )
            return

        print("\n" + "=" * 75)
        print(f"PERMISSIONS FOR: {agent.agent_name}")
        print("=" * 75)

        permissions = self.permissions.get(agent_id, [])

        if not permissions:
            print("No permissions configured.")
            print("=" * 75)
            return

        for permission in permissions:

            print(
                f"Action: {permission.action.value} | "
                f"Effect: {permission.effect.value} | "
                f"Enabled: {permission.enabled} | "
                f"Granted By: {permission.granted_by}"
            )

        print("=" * 75)

    # -----------------------------------------------------
    # Display Check Result
    # -----------------------------------------------------

    @staticmethod
    def display_check_result(
        result: PermissionCheckResult,
    ) -> None:

        print("\n" + "-" * 75)
        print("PERMISSION CHECK RESULT")
        print("-" * 75)

        print(f"Request ID   : {result.request_id}")
        print(f"Agent        : {result.agent_name}")
        print(f"Action       : {result.action.value}")
        print(f"Allowed      : {result.allowed}")
        print(f"Reason       : {result.reason}")

        print("-" * 75)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    logger.info(
        "Starting Exercise 117 - Agent Permissions"
    )

    manager = PermissionManager()

    # -----------------------------------------------------
    # Register Agents
    # -----------------------------------------------------

    agri_agent = manager.register_agent(
        "AgriAssistant"
    )

    support_agent = manager.register_agent(
        "CustomerSupportAgent"
    )

    # -----------------------------------------------------
    # Grant AgriAssistant Permissions
    # -----------------------------------------------------

    manager.grant_permission(
        agent_id=agri_agent.agent_id,
        action=PermissionAction.AGRICULTURE_INFO,
        granted_by="control_plane_admin",
    )

    manager.grant_permission(
        agent_id=agri_agent.agent_id,
        action=PermissionAction.DATA_ANALYSIS,
        granted_by="control_plane_admin",
    )

    manager.grant_permission(
        agent_id=agri_agent.agent_id,
        action=PermissionAction.WEB_SEARCH,
        granted_by="control_plane_admin",
    )

    # Explicitly deny sensitive operation.

    manager.deny_permission(
        agent_id=agri_agent.agent_id,
        action=PermissionAction.DELETE_USER_DATA,
        granted_by="control_plane_admin",
    )

    # -----------------------------------------------------
    # Grant Customer Support Permissions
    # -----------------------------------------------------

    manager.grant_permission(
        agent_id=support_agent.agent_id,
        action=PermissionAction.CUSTOMER_SUPPORT,
        granted_by="support_admin",
    )

    manager.grant_permission(
        agent_id=support_agent.agent_id,
        action=PermissionAction.ISSUE_RESOLUTION,
        granted_by="support_admin",
    )

    # -----------------------------------------------------
    # Display Permissions
    # -----------------------------------------------------

    manager.display_permissions(
        agri_agent.agent_id
    )

    manager.display_permissions(
        support_agent.agent_id
    )

    # -----------------------------------------------------
    # Test Allowed Permission
    # -----------------------------------------------------

    logger.info(
        "Testing allowed agriculture permission"
    )

    result = manager.check_permission(
        agent_id=agri_agent.agent_id,
        action=PermissionAction.AGRICULTURE_INFO,
    )

    manager.display_check_result(result)

    # -----------------------------------------------------
    # Test Denied Permission
    # -----------------------------------------------------

    logger.info(
        "Testing explicitly denied permission"
    )

    result = manager.check_permission(
        agent_id=agri_agent.agent_id,
        action=PermissionAction.DELETE_USER_DATA,
    )

    manager.display_check_result(result)

    # -----------------------------------------------------
    # Test Missing Permission
    # -----------------------------------------------------

    logger.info(
        "Testing action without configured permission"
    )

    result = manager.check_permission(
        agent_id=agri_agent.agent_id,
        action=PermissionAction.SYSTEM_CONFIGURATION,
    )

    manager.display_check_result(result)

    # -----------------------------------------------------
    # Disable Existing Permission
    # -----------------------------------------------------

    logger.info(
        "Disabling agriculture permission"
    )

    manager.disable_permission(
        agent_id=agri_agent.agent_id,
        action=PermissionAction.AGRICULTURE_INFO,
    )

    # -----------------------------------------------------
    # Verify Disabled Permission
    # -----------------------------------------------------

    logger.info(
        "Verifying disabled agriculture permission"
    )

    result = manager.check_permission(
        agent_id=agri_agent.agent_id,
        action=PermissionAction.AGRICULTURE_INFO,
    )

    manager.display_check_result(result)

    # -----------------------------------------------------
    # Final Message
    # -----------------------------------------------------

    logger.info(
        "Exercise 117 - Agent Permissions completed successfully"
    )


if __name__ == "__main__":
    main()