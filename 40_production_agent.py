from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================
# PRODUCTION AGENT
# ============================================================

agent = Agent(
    name="GramSwaram Production Agent",
    model=Ollama(id="llama3.2"),
    instructions=[
        "You are a helpful GramSwaram assistant.",
        "Answer the user's questions clearly.",
        "Do not invent information.",
        "Keep responses concise and useful.",
    ],
)


# ============================================================
# AGENT REQUEST HANDLER
# ============================================================

def handle_request(user_message: str) -> str:

    response = agent.run(user_message)

    return response.content


# ============================================================
# TEST THE RUNTIME
# ============================================================

print("=" * 60)
print("GRAMSWARAM PRODUCTION AGENT")
print("=" * 60)

user_message = """
What is the purpose of GramSwaram?
"""

print("\nUser:")
print(user_message)

result = handle_request(user_message)

print("\nAgent:")
print(result)

print("\n" + "=" * 60)
print("AGENT RUNTIME TEST COMPLETE")
print("=" * 60)