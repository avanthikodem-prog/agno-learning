from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================
# 1. CUSTOMER AND ORDER DATA
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
# 2. DETERMINISTIC CLASSIFICATION
# ============================================================

def classify_customer_issue(message: str) -> dict:

    text = message.lower()

    # Payment issues
    payment_keywords = [
        "refund",
        "payment",
        "charged",
        "charge",
        "billing",
        "duplicate",
        "money back",
    ]

    # Order issues
    order_keywords = [
        "order",
        "order id",
        "shipping",
        "shipped",
        "delivery",
        "delivered",
        "not arrived",
        "order status",
    ]

    # Product issues
    product_keywords = [
        "damaged",
        "defective",
        "wrong product",
        "broken",
        "missing product",
    ]

    # Check payment first
    if any(keyword in text for keyword in payment_keywords):

        return {
            "category": "Payment Issue",
            "issue_type": "Payment Problem",
            "priority": "High",
        }

    # Check order
    elif any(keyword in text for keyword in order_keywords):

        return {
            "category": "Order Issue",
            "issue_type": "Order Status / Delivery Issue",
            "priority": "Medium",
        }

    # Check product
    elif any(keyword in text for keyword in product_keywords):

        return {
            "category": "Product Issue",
            "issue_type": "Product Problem",
            "priority": "Medium",
        }

    # Otherwise general
    else:

        return {
            "category": "General Query",
            "issue_type": "General Question",
            "priority": "Low",
        }


# ============================================================
# 3. CUSTOMER INFORMATION TOOL
# ============================================================

def get_customer_info(customer_name: str) -> str:

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
# 5. HUMAN ESCALATION TOOL
# ============================================================

def escalate_to_human(
    reason: str,
    customer_message: str
) -> str:

    print("\n" + "=" * 60)
    print("HUMAN ESCALATION")
    print("=" * 60)

    print(f"Reason: {reason}")
    print(f"Customer Issue: {customer_message}")

    return (
        "The issue has been escalated to a human support "
        "representative for further assistance."
    )


# ============================================================
# 6. ROUTING
# ============================================================

def route_support_request(category: str) -> str:

    if category == "Order Issue":

        return "Route to Order Support"

    elif category == "Product Issue":

        return "Route to Product Support"

    elif category == "Payment Issue":

        return "Route to Payment Support"

    else:

        return "Route to General Support"


# ============================================================
# 7. CUSTOMER SUPPORT AGENT
# ============================================================

customer_support_agent = Agent(
    name="Complete Customer Support Agent",

    model=Ollama(id="llama3.2"),

    tools=[
        get_customer_info,
        get_order_status,
        escalate_to_human,
    ],

    instructions=[
        "You are a helpful customer support agent.",

        "Use get_customer_info when the customer "
        "provides their name and asks for customer details.",

        "Use get_order_status when the customer "
        "provides an order ID and asks about the order.",

        "You can use multiple tools when necessary.",

        "You cannot issue refunds.",
        "You cannot reverse payments.",
        "You cannot change payment records.",

        "If the customer has a duplicate charge, "
        "refund request, or payment reversal request, "
        "use escalate_to_human.",

        "Never claim that a refund was completed "
        "unless a real refund tool confirms it.",

        "Current Status means the current state of the order.",
        "Expected Delivery means the expected delivery date.",

        "Do not invent information.",

        "Give a clear and professional final response.",
    ],
)


# ============================================================
# 8. TEST CUSTOMER MESSAGE
# ============================================================

customer_message = """
My name is Ravi and my order ID is ORD1001.

I want to know my customer details and the status of my order.
The order has not arrived yet.
"""


# ============================================================
# 9. DISPLAY CUSTOMER MESSAGE
# ============================================================

print("=" * 60)
print("GRAMSWARAM COMPLETE CUSTOMER SUPPORT")
print("=" * 60)

print("\nCUSTOMER MESSAGE")
print("-" * 60)

print(customer_message)


# ============================================================
# 10. CLASSIFY
# ============================================================

classification = classify_customer_issue(
    customer_message
)


# ============================================================
# 11. DISPLAY CLASSIFICATION
# ============================================================

print("\n" + "=" * 60)
print("ISSUE CLASSIFICATION")
print("=" * 60)

print(f"Category: {classification['category']}")
print(f"Issue Type: {classification['issue_type']}")
print(f"Priority: {classification['priority']}")


# ============================================================
# 12. ROUTE
# ============================================================

route = route_support_request(
    classification["category"]
)


print("\n" + "=" * 60)
print("ROUTING")
print("=" * 60)

print(route)


# ============================================================
# 13. HANDLE CUSTOMER REQUEST
# ============================================================

response = customer_support_agent.run(
    customer_message
)


# ============================================================
# 14. FINAL RESPONSE
# ============================================================

print("\n" + "=" * 60)
print("FINAL CUSTOMER SUPPORT RESPONSE")
print("=" * 60)

print(response.content)