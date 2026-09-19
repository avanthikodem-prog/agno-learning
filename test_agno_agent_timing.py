import logging
import time

from agno.agent import Agent
from agno.models.ollama import Ollama


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("agno_agent_timing_test")


MODEL = "llama3.2"
OLLAMA_HOST = "http://127.0.0.1:11434"


def run_test():
    logger.info("Creating direct Agno Agent")

    model = Ollama(
        id=MODEL,
        host=OLLAMA_HOST,
        api_key=None,
        timeout=120,
    )

    agent = Agent(
        id="timing-test-agent",
        name="TimingTestAgent",
        model=model,
        instructions=[
            "You are an AI assistant for agriculture and farmer services.",
            "Give concise, clear and factual answers.",
            "Do not invent facts.",
        ],
        markdown=True,
    )

    question = """
What crops does Ravi grow?

Ravi is a farmer from Telangana.
He grows paddy and cotton.
His farm uses drip irrigation.
He has been farming for 10 years.
"""

    logger.info("Starting direct Agno Agent run")

    start = time.perf_counter()

    response = agent.run(question)

    total_time = time.perf_counter() - start

    print("\n" + "=" * 60)
    print("DIRECT AGNO AGENT TIMING TEST")
    print("=" * 60)
    print(f"Total       : {total_time:.3f} seconds")
    print(f"Response    : {response.content}")
    print("=" * 60)

    logger.info("Direct Agno Agent run completed")


if __name__ == "__main__":
    run_test()