import logging
import time
import uuid

from agno.agent import Agent
from agno.models.ollama import Ollama


# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agent_runtime_tools")


# ---------------------------------------------------------
# Runtime
# ---------------------------------------------------------

class AgentRuntime:
    """
    Runtime responsible for executing an Agno agent
    with tool execution.
    """

    def __init__(self):
        self.execution_id = str(uuid.uuid4())
        self.status = "CREATED"
        self.start_time = None
        self.end_time = None
        self.tool_call_count = 0

        logger.info(
            "Runtime created | execution_id=%s",
            self.execution_id,
        )

        # -------------------------------------------------
        # Runtime Tool
        # -------------------------------------------------

        def add_numbers(a: float, b: float) -> float:
            """
            Add two numbers and return the result.

            This function is exposed to the AI agent
            as a tool.
            """

            self.tool_call_count += 1

            logger.info(
                "Tool called | name=add_numbers | a=%s | b=%s",
                a,
                b,
            )

            result = a + b

            logger.info(
                "Tool completed | name=add_numbers | result=%s",
                result,
            )

            return result

        self.add_numbers = add_numbers

        # -------------------------------------------------
        # Agno Agent
        # -------------------------------------------------

        self.agent = Agent(
            model=Ollama(id="llama3.2"),
            tools=[self.add_numbers],
            instructions=[
                "You are a helpful AI assistant.",
                "When the user asks for arithmetic calculation, "
                "use the available add_numbers tool.",
                "Do not calculate arithmetic yourself when "
                "the tool can perform it.",
            ],
        )

        logger.info("Agno agent initialized with runtime tool")


    # ---------------------------------------------------------
    # Start Runtime
    # ---------------------------------------------------------

    def start(self):
        self.status = "RUNNING"
        self.start_time = time.time()

        logger.info(
            "Runtime started | execution_id=%s",
            self.execution_id,
        )


    # ---------------------------------------------------------
    # Execute Agent
    # ---------------------------------------------------------

    def execute(self, user_message: str) -> str:
        logger.info(
            "Agent execution started | message=%s",
            user_message,
        )

        try:
            response = self.agent.run(user_message)

            logger.info("Agent execution completed")

            return response.content

        except Exception as exc:
            self.status = "FAILED"

            logger.exception(
                "Agent execution failed | error=%s",
                exc,
            )

            raise


    # ---------------------------------------------------------
    # Complete Runtime
    # ---------------------------------------------------------

    def complete(self):
        self.status = "COMPLETED"
        self.end_time = time.time()

        duration = self.end_time - self.start_time

        logger.info(
            "Runtime completed | execution_id=%s | "
            "duration=%.2f seconds | tool_calls=%s",
            self.execution_id,
            duration,
            self.tool_call_count,
        )


    # ---------------------------------------------------------
    # Display Runtime Information
    # ---------------------------------------------------------

    def display_runtime(self):
        duration = None

        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time

        print("\n" + "=" * 60)
        print("AGENT RUNTIME TOOL EXECUTION")
        print("=" * 60)

        print(f"Execution ID : {self.execution_id}")
        print(f"Status       : {self.status}")
        print(f"Tool Calls   : {self.tool_call_count}")

        if duration is not None:
            print(f"Duration     : {duration:.2f} seconds")

        print("=" * 60)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    logger.info("Starting Exercise 107")

    runtime = AgentRuntime()

    runtime.start()

    user_message = (
        "Use the add_numbers tool to calculate 125 + 75. "
        "Return the final answer clearly."
    )

    logger.info(
        "Sending request to runtime: %s",
        user_message,
    )

    response = runtime.execute(user_message)

    runtime.complete()

    print("\nAI RESPONSE:")
    print(response)

    runtime.display_runtime()

    logger.info("Exercise 107 completed successfully")


# ---------------------------------------------------------
# Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()