from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools import tool


@tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression."""

    print("\n🔧 SPAN: Calculator Tool")
    print("Expression:", expression)

    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Calculation error: {e}"


agent = Agent(
    name="Trace Demo Agent",
    model=Ollama(id="llama3.2"),
    tools=[calculate],
    instructions="""
    You are a calculator assistant.

    Always use the calculate tool for mathematical calculations.
    """,
)


print("========== TRACE START ==========")

response = agent.run(
    "Calculate 250 * 20 + 100"
)

print("\n========== TRACE END ==========")

print("\n========== FINAL RESPONSE ==========")
print(response.content)

print("\n========== RUN INFORMATION ==========")
print("Run ID:", response.run_id)
print("Session ID:", response.session_id)