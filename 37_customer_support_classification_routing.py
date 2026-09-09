from typing import Literal

from pydantic import BaseModel, Field

from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================
# 1. STRUCTURED ISSUE CLASSIFICATION
# ============================================================

class SupportClassification(BaseModel):
    category: Literal[
        "Order Issue",
        "Product Issue",
        "General Query",
    ] = Field(description="Main category of the customer issue.")

    priority: Literal[
        "Low",
        "Medium",
        "High",
    ] = Field(description="Priority of the customer issue.")

    issue_type: str = Field(
        description="Specific type of customer issue."
    )


# ============================================================
# 2. CLASSIFICATION AGENT
# ============================================================

classification_agent = Agent(
    name="Customer Support Classification Agent",
    model=Ollama(id="llama3.2"),
    output_schema=SupportClassification,
    instructions=[
        "Classify the customer's message into exactly one category.",

        "Order Issue means problems related to orders, "
        "delivery, shipping, or order status.",

        "Product Issue means problems related to a product, "
        "such as damaged product, wrong product, or defective product.",

        "General Query means questions that do not belong "
        "to Order Issue or Product Issue.",

        "Use High priority for urgent problems.",
        "Use Medium priority for normal support problems.",
        "Use Low priority for simple information questions.",

        "Give a specific issue type.",
    ],
)


# ============================================================
# 3. CUSTOMER DATABASE
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
}


# ============================================================
# 4. ORDER DATABASE
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
}


# ============================================================
# 5. CUSTOMER INFORMATION TOOL
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
# 6. ORDER STATUS TOOL
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
# 7. CUSTOMER SUPPORT AGENT
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

        "Use get_order_status when an order ID is provided.",
        "Use get_customer_info when a customer name is provided "
        "and customer information is requested.",

        "Do not invent customer or order information.",

        "Current Status means the current state of the order.",
        "Expected Delivery means the expected delivery date.",

        "Give a clear, accurate, and professional response.",
    ],
)


# ============================================================
# 8. ROUTING FUNCTION
# ============================================================

def route_support_request(
    classification: SupportClassification
) -> str:

    if classification.category == "Order Issue":
        return "Route to Order Support"

    elif classification.category == "Product Issue":
        return "Route to Product Support"

    else:
        return "Route to General Support"


# ============================================================
# 9. CUSTOMER MESSAGE
# ============================================================

customer_message = """
My name is Ravi and my order ID is ORD1001.
My order has not arrived yet. Please check what is happening
with my order.
"""


# ============================================================
# 10. DISPLAY CUSTOMER MESSAGE
# ============================================================

print("=" * 70)
print("GRAMSWARAM CUSTOMER SUPPORT")
print("CLASSIFICATION + TOOLS + ROUTING")
print("=" * 70)

print("\nCustomer Message:")
print(customer_message)


# ============================================================
# 11. CLASSIFY CUSTOMER ISSUE
# ============================================================

classification_response = classification_agent.run(
    customer_message
)

classification = classification_response.content


# ============================================================
# 12. DISPLAY CLASSIFICATION
# ============================================================

print("\n" + "=" * 70)
print("ISSUE CLASSIFICATION")
print("=" * 70)

print(f"Category: {classification.category}")
print(f"Issue Type: {classification.issue_type}")
print(f"Priority: {classification.priority}")


# ============================================================
# 13. ROUTE CUSTOMER REQUEST
# ============================================================

route = route_support_request(classification)

print("\n" + "=" * 70)
print("ROUTING")
print("=" * 70)

print(route)


# ============================================================
# 14. RUN CUSTOMER SUPPORT AGENT
# ============================================================

support_response = customer_support_agent.run(
    customer_message
)


# ============================================================
# 15. DISPLAY FINAL RESPONSE
# ============================================================

print("\n" + "=" * 70)
print("FINAL CUSTOMER SUPPORT RESPONSE")
print("=" * 70)

print(support_response.content)


# ============================================================
# 16. COMPLETED
# ============================================================

print("\n" + "=" * 70)
print("CUSTOMER SUPPORT WORKFLOW COMPLETED")
print("=" * 70)