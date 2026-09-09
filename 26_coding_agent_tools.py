from pathlib import Path

from agno.agent import Agent
from agno.models.ollama import Ollama


# Workspace where the Coding Agent is allowed to work
WORKSPACE = Path("coding_agent_workspace")


def list_files() -> str:
    """List files inside the coding agent workspace."""
    files = list(WORKSPACE.iterdir())

    if not files:
        return "The workspace is empty."

    return "\n".join(file.name for file in files)


def read_file(filename: str) -> str:
    """Read a file from the coding agent workspace."""
    file_path = WORKSPACE / filename

    if not file_path.exists():
        return f"File '{filename}' does not exist."

    if not file_path.is_file():
        return f"'{filename}' is not a file."

    return file_path.read_text(encoding="utf-8")


def write_file(filename: str, content: str) -> str:
    """Create or overwrite a file inside the coding agent workspace."""
    file_path = WORKSPACE / filename

    file_path.write_text(content, encoding="utf-8")

    return f"File '{filename}' was created successfully."


coding_agent = Agent(
    name="Coding Agent",
    model=Ollama(id="llama3.2"),
    tools=[
        list_files,
        read_file,
        write_file,
    ],
    instructions=[
        "You are a coding agent.",
        "You can work with files inside the coding_agent_workspace directory.",
        "Use the file tools when you need to inspect or modify files.",
        "Never access files outside the coding_agent_workspace.",
        "When asked to create a file, use the write_file tool.",
        "When asked to inspect a file, use the read_file tool.",
        "When asked to list files, use the list_files tool.",
    ],
)


print("=" * 60)
print("AGNO CODING AGENT - FILE TOOLS")
print("=" * 60)

response = coding_agent.run(
    """
Create a file called calculator.py inside the workspace.

The Python program should:
1. Define a function called add.
2. The function should accept two numbers.
3. Return their sum.
4. Print an example result.

Use the file tool to create the file.
After creating it, tell me what you did.
"""
)

print("\nCoding Agent Response:")
print(response.content)


print("\n" + "=" * 60)
print("WORKSPACE FILES")
print("=" * 60)

print(list_files())