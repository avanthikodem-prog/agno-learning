from agno.agent import Agent
from agno.models.ollama import Ollama


def escalate_to_human(
    reason: str,
    customer_message: str
) -> str:
    """
    Escalate a customer issue to a human support representative.
    """

    print("\n" + "=" * 60)
    print("HUMAN ESCALATION")
    print("=" * 60)

    print(f"Reason: {reason}")
    print(f"Customer Issue: {customer_message}")

    return (
        "This issue has been escalated to a human support representative. "
        "A support representative will review the issue and assist you."
    )


customer_support_agent = Agent(
    name="Customer Support Agent",
    model=Ollama(id="llama3.2"),
    tools=[escalate_to_human],
    instructions=[
        "You are a helpful customer support agent.",
        "Understand the customer's problem carefully.",
        "Answer simple questions when you have enough information.",
        "Do not invent information.",
        "Do not promise actions that you cannot perform.",
        "You cannot issue refunds.",
        "You cannot reverse payments.",
        "You cannot manually change customer account information.",
        "If the customer requests a refund, payment reversal, "
        "or another action that requires human intervention, "
        "use the escalate_to_human tool.",
        "After escalation, clearly tell the customer that "
        "the issue has been escalated to human support.",
    ],
)


print("=" * 60)
print("GRAMSWARAM CUSTOMER SUPPORT")
print("HUMAN ESCALATION TEST")
print("=" * 60)


customer_message = """
I was charged ₹5,000 twice for the same order.
I want my money back.
"""

print("\nCustomer Message:")
print(customer_message)


response = customer_support_agent.run(customer_message)


print("\n" + "=" * 60)
print("FINAL CUSTOMER SUPPORT RESPONSE")
print("=" * 60)

print(response.content)