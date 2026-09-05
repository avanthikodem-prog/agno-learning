from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.db.sqlite import SqliteDb
from agno.tools import tool


@tool
def calculate(expression: str) -> str:
    """Calculate a mathematical expression."""

    print(f"🔧 Calculator tool called with: {expression}")

    try:
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Calculation error: {e}"


db = SqliteDb(
    db_file="observability.db"
)


agent = Agent(
    name="Observable Calculator Agent",
    model=Ollama(id="llama3.2"),
    tools=[calculate],
    db=db,
    instructions="""
    You are a calculator assistant.

    When the user asks for a mathematical calculation,
    use the calculate tool.

    Pass the complete mathematical expression to the tool.
    """,
)


response = agent.run(
    "Calculate 125 * 48 + 350"
)


print("\n========== FINAL RESPONSE ==========\n")
print(response.content)

print("\n========== RUN INFORMATION ==========\n")
print("Run ID:", response.run_id)
print("Session ID:", response.session_id)

print("\n========== DATABASE ==========\n")
print("Run information is stored in observability.db")