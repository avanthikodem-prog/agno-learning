import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional
from uuid import uuid4


# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agent_configuration")


# ---------------------------------------------------------
# Agent Environment
# ---------------------------------------------------------

class Environment(Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


# ---------------------------------------------------------
# Agent Configuration
# ---------------------------------------------------------

@dataclass
class AgentConfiguration:
    config_id: str
    agent_id: str
    model: str
    temperature: float
    max_tokens: int
    system_prompt: str
    tools: List[str] = field(default_factory=list)
    language: str = "English"
    environment: Environment = Environment.DEVELOPMENT
    enabled: bool = True


# ---------------------------------------------------------
# Configuration Manager
# ---------------------------------------------------------

class ConfigurationManager:

    def __init__(self):
        self.configurations = {}

        logger.info("Configuration Manager initialized")

    # -----------------------------------------------------
    # Create Configuration
    # -----------------------------------------------------

    def create_configuration(
        self,
        agent_id: str,
        model: str,
        temperature: float,
        max_tokens: int,
        system_prompt: str,
        tools: Optional[List[str]] = None,
        language: str = "English",
        environment: Environment = Environment.DEVELOPMENT,
    ) -> AgentConfiguration:

        if tools is None:
            tools = []

        self._validate_configuration(
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
        )

        config = AgentConfiguration(
            config_id=str(uuid4()),
            agent_id=agent_id,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
            system_prompt=system_prompt,
            tools=tools,
            language=language,
            environment=environment,
        )

        self.configurations[agent_id] = config

        logger.info(
            "Configuration created for agent_id=%s | model=%s | environment=%s",
            agent_id,
            model,
            environment.value,
        )

        return config

    # -----------------------------------------------------
    # Get Configuration
    # -----------------------------------------------------

    def get_configuration(
        self,
        agent_id: str,
    ) -> Optional[AgentConfiguration]:

        config = self.configurations.get(agent_id)

        if config:
            logger.info(
                "Configuration retrieved for agent_id=%s",
                agent_id,
            )
        else:
            logger.warning(
                "Configuration not found for agent_id=%s",
                agent_id,
            )

        return config

    # -----------------------------------------------------
    # Update Configuration
    # -----------------------------------------------------

    def update_configuration(
        self,
        agent_id: str,
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        system_prompt: Optional[str] = None,
        tools: Optional[List[str]] = None,
        language: Optional[str] = None,
        environment: Optional[Environment] = None,
        enabled: Optional[bool] = None,
    ) -> Optional[AgentConfiguration]:

        config = self.configurations.get(agent_id)

        if not config:
            logger.warning(
                "Cannot update configuration. Agent not found: %s",
                agent_id,
            )
            return None

        new_temperature = (
            temperature
            if temperature is not None
            else config.temperature
        )

        new_max_tokens = (
            max_tokens
            if max_tokens is not None
            else config.max_tokens
        )

        new_system_prompt = (
            system_prompt
            if system_prompt is not None
            else config.system_prompt
        )

        self._validate_configuration(
            temperature=new_temperature,
            max_tokens=new_max_tokens,
            system_prompt=new_system_prompt,
        )

        if model is not None:
            config.model = model

        if temperature is not None:
            config.temperature = temperature

        if max_tokens is not None:
            config.max_tokens = max_tokens

        if system_prompt is not None:
            config.system_prompt = system_prompt

        if tools is not None:
            config.tools = tools

        if language is not None:
            config.language = language

        if environment is not None:
            config.environment = environment

        if enabled is not None:
            config.enabled = enabled

        logger.info(
            "Configuration updated successfully for agent_id=%s",
            agent_id,
        )

        return config

    # -----------------------------------------------------
    # Validate Configuration
    # -----------------------------------------------------

    @staticmethod
    def _validate_configuration(
        temperature: float,
        max_tokens: int,
        system_prompt: str,
    ) -> None:

        if temperature < 0 or temperature > 2:
            raise ValueError(
                "Temperature must be between 0 and 2"
            )

        if max_tokens <= 0:
            raise ValueError(
                "max_tokens must be greater than 0"
            )

        if not system_prompt.strip():
            raise ValueError(
                "System prompt cannot be empty"
            )

        logger.info("Configuration validation successful")

    # -----------------------------------------------------
    # Display Configuration
    # -----------------------------------------------------

    def display_configuration(
        self,
        agent_id: str,
    ) -> None:

        config = self.get_configuration(agent_id)

        if not config:
            return

        print("\n" + "=" * 60)
        print("AGENT CONFIGURATION")
        print("=" * 60)

        print(f"Configuration ID : {config.config_id}")
        print(f"Agent ID         : {config.agent_id}")
        print(f"Model            : {config.model}")
        print(f"Temperature      : {config.temperature}")
        print(f"Max Tokens       : {config.max_tokens}")
        print(f"System Prompt    : {config.system_prompt}")
        print(f"Tools            : {config.tools}")
        print(f"Language         : {config.language}")
        print(f"Environment      : {config.environment.value}")
        print(f"Enabled          : {config.enabled}")

        print("=" * 60)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    logger.info("Starting Exercise 115 - Agent Configuration")

    manager = ConfigurationManager()

    # -----------------------------------------------------
    # Create Agent ID
    # -----------------------------------------------------

    agent_id = str(uuid4())

    logger.info("Created agent_id=%s", agent_id)

    # -----------------------------------------------------
    # Create Initial Configuration
    # -----------------------------------------------------

    manager.create_configuration(
        agent_id=agent_id,
        model="llama3.2",
        temperature=0.7,
        max_tokens=1000,
        system_prompt=(
            "You are an AI assistant that provides "
            "helpful and accurate information."
        ),
        tools=[
            "web_search",
            "calculator",
        ],
        language="English",
        environment=Environment.DEVELOPMENT,
    )

    # -----------------------------------------------------
    # Display Initial Configuration
    # -----------------------------------------------------

    logger.info("Displaying initial configuration")

    manager.display_configuration(agent_id)

    # -----------------------------------------------------
    # Update Configuration
    # -----------------------------------------------------

    logger.info("Updating agent configuration")

    manager.update_configuration(
        agent_id=agent_id,
        temperature=0.3,
        max_tokens=2000,
        tools=[
            "web_search",
            "calculator",
            "data_analysis",
        ],
        language="English",
        environment=Environment.STAGING,
    )

    # -----------------------------------------------------
    # Display Updated Configuration
    # -----------------------------------------------------

    logger.info("Displaying updated configuration")

    manager.display_configuration(agent_id)

    # -----------------------------------------------------
    # Retrieve Configuration
    # -----------------------------------------------------

    logger.info("Retrieving configuration")

    config = manager.get_configuration(agent_id)

    if config:
        logger.info(
            "Final configuration verified | model=%s | temperature=%s | environment=%s",
            config.model,
            config.temperature,
            config.environment.value,
        )

    logger.info(
        "Exercise 115 - Agent Configuration completed successfully"
    )


if __name__ == "__main__":
    main()