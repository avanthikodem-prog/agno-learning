from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================
# 1. CREATE CUSTOMER SUPPORT AGENT
# ============================================================

customer_support_agent = Agent(
    name="Customer Support Agent",
    model=Ollama(id="llama3.2"),
    instructions=[
        "You are a helpful customer support agent.",
        "Understand the customer's problem clearly.",
        "Respond politely and professionally.",
        "Give a useful solution when possible.",
        "If you do not have enough information, ask a clear question.",
        "Do not invent information.",
    ],
)


# ============================================================
# 2. CUSTOMER MESSAGE
# ============================================================

customer_message = """
I placed an order yesterday, but I still have not received it.
Can you help me?
"""


# ============================================================
# 3. DISPLAY INPUT
# ============================================================

print("=" * 60)
print("GRAMSWARAM CUSTOMER SUPPORT AGENT")
print("=" * 60)

print("\nCustomer Message:")
print(customer_message)


# ============================================================
# 4. RUN AGENT
# ============================================================

response = customer_support_agent.run(
    customer_message
)


# ============================================================
# 5. DISPLAY RESPONSE
# ============================================================

print("\n" + "=" * 60)
print("CUSTOMER SUPPORT RESPONSE")
print("=" * 60)

print(response.content)