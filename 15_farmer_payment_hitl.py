from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools import tool


@tool(requires_confirmation=True)
def make_farmer_payment(
    farmer_name: str,
    amount: float,
) -> str:
    """Make a payment to a farmer."""

    print("💰 PAYMENT TOOL EXECUTED!")

    return (
        f"Payment of ₹{amount} successfully made "
        f"to farmer {farmer_name}."
    )


agent = Agent(
    name="Farmer Payment Assistant",
    model=Ollama(id="llama3.2"),
    tools=[make_farmer_payment],
    instructions="""
    You are a farmer payment assistant.

    When the user asks to make a payment to a farmer,
    use the make_farmer_payment tool.

    Always use the tool for payment requests.
    """
)


run = agent.run(
    "Pay ₹5000 to farmer Ravi."
)


if run.is_paused:
    print("\n⏸️ Payment requires human approval.")

    requirement = run.active_requirements[0]

    # ------------------------------------------------
    # HUMAN DECISION
    # ------------------------------------------------

    # APPROVE:
    # requirement.confirm()

    # REJECT:
    requirement.reject()

    print("\n👤 Human approval: REJECTED")

    print("\n❌ Payment was rejected by the human.")