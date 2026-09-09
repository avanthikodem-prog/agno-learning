from agno.agent import Agent
from agno.models.ollama import Ollama


coding_agent = Agent(
    name="Coding Agent",
    model=Ollama(id="llama3.2"),
    instructions=[
        "You are a coding assistant.",
        "Help the user write, understand, and debug code.",
        "Always provide clear and correct code.",
        "Explain the code briefly when useful.",
    ],
)


print("=" * 60)
print("AGNO CODING AGENT")
print("=" * 60)

response = coding_agent.run(
    """
Create a Python program that calculates the factorial of a number.

Requirements:
1. Use a function called factorial.
2. Accept a number from the user.
3. Calculate the factorial.
4. Print the result.
5. Handle negative numbers appropriately.
"""
)

print("\nCoding Agent Response:")
print(response.content)