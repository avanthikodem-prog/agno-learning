from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================
# 1. SIMULATED ORDER DATABASE
# ============================================================

orders = {
    "ORD1001": {
        "customer": "Ravi",
        "status": "Shipped",
        "expected_delivery": "Tomorrow",
        "product": "Rice Seeds",
    },
    "ORD1002": {
        "customer": "Sita",
        "status": "Delivered",
        "expected_delivery": "Yesterday",
        "product": "Fertilizer",
    },
    "ORD1003": {
        "customer": "Kiran",
        "status": "Processing",
        "expected_delivery": "In 3 days",
        "product": "Pesticide",
    },
}


# ============================================================
# 2. ORDER STATUS TOOL
# ============================================================

def get_order_status(order_id: str) -> str:
    """
    Get the current status and delivery information
    for a customer order.
    """

    order = orders.get(order_id)

    if order is None:
        return f"Order {order_id} was not found."

    return (
        f"Order ID: {order_id}\n"
        f"Customer: {order['customer']}\n"
        f"Product: {order['product']}\n"
        f"Current Status: {order['status']}\n"
        f"Expected Delivery: {order['expected_delivery']}"
    )


# ============================================================
# 3. CUSTOMER SUPPORT AGENT
# ============================================================

customer_support_agent = Agent(
    name="Customer Support Agent",
    model=Ollama(id="llama3.2"),
    tools=[get_order_status],
    instructions=[
        "You are a helpful customer support agent.",

        "Understand the customer's problem clearly.",

        "When the customer provides an order ID, "
        "use the get_order_status tool.",

        "Always use the tool when an order ID is available.",

        "IMPORTANT:",
        "Current Status means the current state of the order.",
        "Expected Delivery means the expected delivery date.",
        "Never combine or reinterpret these two fields.",

        "If Current Status is Shipped, say the order is shipped.",
        "If Expected Delivery is Tomorrow, say delivery is expected tomorrow.",

        "Do not invent order information.",

        "Give the customer a clear, accurate, "
        "and professional response.",
    ],
)


# ============================================================
# 4. CUSTOMER MESSAGE
# ============================================================

customer_message = """
My order ORD1001 has not arrived yet.
Can you check the status of my order?
"""


# ============================================================
# 5. DISPLAY CUSTOMER MESSAGE
# ============================================================

print("=" * 60)
print("GRAMSWARAM CUSTOMER SUPPORT AGENT")
print("=" * 60)

print("\nCustomer Message:")
print(customer_message)


# ============================================================
# 6. RUN AGENT
# ============================================================

response = customer_support_agent.run(
    customer_message
)


# ============================================================
# 7. DISPLAY RESPONSE
# ============================================================

print("\n" + "=" * 60)
print("CUSTOMER SUPPORT RESPONSE")
print("=" * 60)

print(response.content)