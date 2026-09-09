from pathlib import Path
import subprocess
import ast

from agno.agent import Agent
from agno.models.ollama import Ollama


WORKSPACE = Path("coding_agent_workspace")


def read_file(filename: str) -> str:
    file_path = WORKSPACE / filename

    if not file_path.exists():
        return f"File '{filename}' does not exist."

    return file_path.read_text(encoding="utf-8")


def write_file(filename: str, content: str) -> str:
    file_path = WORKSPACE / filename

    file_path.write_text(content, encoding="utf-8")

    return f"File '{filename}' was written successfully."


def run_python_file(filename: str) -> str:
    file_path = WORKSPACE / filename

    result = subprocess.run(
        ["python", str(file_path)],
        capture_output=True,
        text=True,
        timeout=10,
    )

    output = result.stdout

    if result.stderr:
        output += "\nERROR:\n" + result.stderr

    return output


def validate_python_code(code: str) -> str:
    try:
        ast.parse(code)
        return "VALID"
    except SyntaxError as e:
        return f"INVALID: {e}"


coding_agent = Agent(
    name="Debugging Agent",
    model=Ollama(id="llama3.2"),
    instructions=[
        "You are a Python debugging agent.",
        "Analyze Python errors carefully.",
        "Identify the cause of the error.",
        "Generate corrected Python code.",
        "Return ONLY valid Python code when asked for corrected code.",
        "Do not use markdown.",
        "Do not use ``` symbols.",
    ],
)


print("=" * 60)
print("AGNO CODING AGENT - DEBUGGING")
print("=" * 60)


# --------------------------------------------------
# 1. Create intentionally buggy program
# --------------------------------------------------

buggy_code = """
def divide(a, b):
    return a / b

print(divide(10, 0))
"""

print("\n1. CREATING BUGGY PROGRAM")
print("-" * 60)

write_file("buggy_calculator.py", buggy_code)

print(read_file("buggy_calculator.py"))


# --------------------------------------------------
# 2. Run buggy program
# --------------------------------------------------

print("\n2. RUNNING BUGGY PROGRAM")
print("-" * 60)

error_output = run_python_file("buggy_calculator.py")

print(error_output)


# --------------------------------------------------
# 3. Ask Coding Agent to fix it
# --------------------------------------------------

print("\n3. ASKING CODING AGENT TO DEBUG")
print("-" * 60)

current_code = read_file("buggy_calculator.py")

response = coding_agent.run(
    f"""
Debug this Python program.

Current code:

{current_code}

Execution output:

{error_output}

Requirements:

1. Identify the cause of the error.
2. Fix the program.
3. The divide function should safely handle division by zero.
4. Return a meaningful message when b is zero.
5. Return the normal division result otherwise.

Return ONLY the complete corrected Python code.
Do not include explanations.
Do not use markdown.
Do not use ``` symbols.
"""
)

fixed_code = response.content.strip()

print(fixed_code)


# --------------------------------------------------
# 4. Validate corrected code
# --------------------------------------------------

print("\n4. VALIDATING FIXED CODE")
print("-" * 60)

validation = validate_python_code(fixed_code)

print(validation)


# --------------------------------------------------
# 5. Save corrected code
# --------------------------------------------------

if validation == "VALID":

    print("\n5. SAVING FIXED CODE")
    print("-" * 60)

    write_file("buggy_calculator.py", fixed_code)

    print("Fixed code saved successfully.")


    # --------------------------------------------------
    # 6. Run fixed code
    # --------------------------------------------------

    print("\n6. RUNNING FIXED CODE")
    print("-" * 60)

    final_output = run_python_file("buggy_calculator.py")

    print(final_output)


    # --------------------------------------------------
    # 7. Final code
    # --------------------------------------------------

    print("\n" + "=" * 60)
    print("FINAL FIXED CODE")
    print("=" * 60)

    print(read_file("buggy_calculator.py"))

else:

    print("\nFixed code is invalid.")
    print("The code was NOT saved.")