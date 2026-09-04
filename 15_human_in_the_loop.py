from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools import tool


@tool(requires_confirmation=True)
def send_message(message: str) -> str:
    """Send an important message."""

    print("🔧 SEND_MESSAGE TOOL EXECUTED!")

    return f"Message actually sent: {message}"


agent = Agent(
    name="HITL Assistant",
    model=Ollama(id="llama3.2"),
    tools=[send_message],
    instructions="""
    You are a helpful assistant.

    When the user asks you to send a message,
    use the send_message tool.
    """
)


run = agent.run(
    "Send the message 'Hello Ravi, your order is ready.'"
)


if run.is_paused:
    print("\nRun paused for human approval.")

    requirement = run.active_requirements[0]

    print("Rejecting tool call...")

    requirement.reject()

    continued_run = agent.continue_run(
        run_response=run
    )

    print("\nFinal response:")
    print(continued_run.content)