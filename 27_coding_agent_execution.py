from pathlib import Path
import subprocess
import ast

from agno.agent import Agent
from agno.models.ollama import Ollama


WORKSPACE = Path("coding_agent_workspace")


def read_file(filename: str) -> str:
    """Read a file from the coding agent workspace."""
    file_path = WORKSPACE / filename

    if not file_path.exists():
        return f"File '{filename}' does not exist."

    return file_path.read_text(encoding="utf-8")


def write_file(filename: str, content: str) -> str:
    """Create or update a file inside the coding agent workspace."""
    file_path = WORKSPACE / filename

    file_path.write_text(content, encoding="utf-8")

    return f"File '{filename}' was written successfully."


def validate_python_code(code: str) -> str:
    """Check whether the generated code has valid Python syntax."""
    try:
        ast.parse(code)
        return "VALID"
    except SyntaxError as e:
        return f"INVALID: {e}"


def run_python_file(filename: str) -> str:
    """Run a Python file inside the coding agent workspace."""
    file_path = WORKSPACE / filename

    if not file_path.exists():
        return f"File '{filename}' does not exist."

    result = subprocess.run(
        ["python", str(file_path)],
        capture_output=True,
        text=True,
        timeout=10,
    )

    output = result.stdout

    if result.stderr:
        output += "\nERROR:\n" + result.stderr

    return output if output else "Program executed successfully with no output."


coding_agent = Agent(
    name="Coding Agent",
    model=Ollama(id="llama3.2"),
    instructions=[
        "You are a coding agent.",
        "Generate correct Python code.",
        "When asked for code, return ONLY the Python code.",
        "Do not include explanations.",
        "Do not include markdown.",
        "Do not include ``` code fences.",
    ],
)


print("=" * 60)
print("AGNO CODING AGENT - CODE VALIDATION")
print("=" * 60)


# --------------------------------------------------
# 1. Read existing file
# --------------------------------------------------

print("\n1. EXISTING FILE")
print("-" * 60)

existing_code = read_file("calculator.py")
print(existing_code)


# --------------------------------------------------
# 2. Ask the LLM to generate updated code
# --------------------------------------------------

print("\n2. ASKING CODING AGENT FOR UPDATED CODE")
print("-" * 60)

response = coding_agent.run(
    """
Create the complete Python code for calculator.py.

Requirements:

1. Define add(a, b).
2. add(a, b) returns a + b.
3. Define subtract(a, b).
4. subtract(a, b) returns a - b.
5. Print add(5, 7).
6. Print subtract(5, 7).

IMPORTANT:
Return ONLY valid Python code.
Do not explain anything.
Do not use markdown.
Do not use ``` symbols.
"""
)

generated_code = response.content.strip()

print(generated_code)


# --------------------------------------------------
# 3. Validate generated code
# --------------------------------------------------

print("\n3. VALIDATING PYTHON CODE")
print("-" * 60)

validation = validate_python_code(generated_code)

print(validation)


# --------------------------------------------------
# 4. Save only if valid
# --------------------------------------------------

if validation == "VALID":

    print("\n4. SAVING CODE")
    print("-" * 60)

    print(write_file("calculator.py", generated_code))


    # --------------------------------------------------
    # 5. Execute the code
    # --------------------------------------------------

    print("\n5. RUNNING CODE")
    print("-" * 60)

    output = run_python_file("calculator.py")

    print(output)


    # --------------------------------------------------
    # 6. Final file
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL FILE CONTENT")
    print("=" * 60)

    print(read_file("calculator.py"))

else:

    print("\n4. CODE WAS NOT SAVED")
    print("-" * 60)
    print("The coding agent generated invalid Python code.")
    print("We prevented invalid code from being written.")