from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================
# 1. SIMULATED CUSTOMER DATABASE
# ============================================================

customers = {
    "Ravi": {
        "phone": "9876543210",
        "location": "Nizamabad",
        "membership": "Regular",
    },
    "Sita": {
        "phone": "9876543211",
        "location": "Hyderabad",
        "membership": "Premium",
    },
    "Kiran": {
        "phone": "9876543212",
        "location": "Warangal",
        "membership": "Regular",
    },
}


# ============================================================
# 2. SIMULATED ORDER DATABASE
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
# 3. CUSTOMER INFORMATION TOOL
# ============================================================

def get_customer_info(customer_name: str) -> str:
    """
    Get customer information.
    """

    customer = customers.get(customer_name)

    if customer is None:
        return f"Customer {customer_name} was not found."

    return (
        f"Customer Name: {customer_name}\n"
        f"Phone: {customer['phone']}\n"
        f"Location: {customer['location']}\n"
        f"Membership: {customer['membership']}"
    )


# ============================================================
# 4. ORDER STATUS TOOL
# ============================================================

def get_order_status(order_id: str) -> str:
    """
    Get order information.
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
# 5. CUSTOMER SUPPORT AGENT
# ============================================================

customer_support_agent = Agent(
    name="Customer Support Agent",
    model=Ollama(id="llama3.2"),
    tools=[
        get_customer_info,
        get_order_status,
    ],
    instructions=[
        "You are a helpful customer support agent.",

        "Understand the customer's request carefully.",

        "Use get_order_status when the customer asks "
        "about an order and provides an order ID.",

        "Use get_customer_info when the customer asks "
        "about customer information and provides a customer name.",

        "You may use more than one tool when the customer "
        "asks for different types of information.",

        "Do not invent customer or order information.",

        "IMPORTANT:",
        "Current Status means the current state of the order.",
        "Expected Delivery means the expected delivery date.",
        "Never combine or reinterpret these fields.",

        "Give a clear, accurate, and professional response.",
    ],
)


# ============================================================
# 6. CUSTOMER MESSAGE
# ============================================================

customer_message = """
My name is Ravi and my order ID is ORD1001.
Please check my customer details and also tell me the status
of my order.
"""


# ============================================================
# 7. DISPLAY CUSTOMER MESSAGE
# ============================================================

print("=" * 60)
print("GRAMSWARAM CUSTOMER SUPPORT - MULTIPLE TOOLS")
print("=" * 60)

print("\nCustomer Message:")
print(customer_message)


# ============================================================
# 8. RUN AGENT
# ============================================================

response = customer_support_agent.run(
    customer_message
)


# ============================================================
# 9. DISPLAY RESPONSE
# ============================================================

print("\n" + "=" * 60)
print("CUSTOMER SUPPORT RESPONSE")
print("=" * 60)

print(response.content)