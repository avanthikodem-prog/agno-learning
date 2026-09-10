import logging

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.websearch import WebSearchTools


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_deep_research")


# ---------------------------------------------------------
# Create Deep Research Agent
# ---------------------------------------------------------

def create_research_agent() -> Agent:
    """Create an Agno agent capable of web research."""

    logger.info("Creating Deep Research Agent")

    agent = Agent(
        model=Ollama(id="llama3.2"),
        tools=[
            WebSearchTools()
        ],
        instructions=[
            "You are a research assistant.",
            "Research the user's question using web search.",
            "Use multiple sources when appropriate.",
            "Prefer reliable and relevant sources.",
            "Summarize the information clearly.",
            "Distinguish facts from opinions.",
            "Include source links when available.",
            "Do not invent information.",
        ],
        markdown=True,
    )

    logger.info("Deep Research Agent created successfully")

    return agent


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    logger.info("Starting Basic Deep Research exercise")

    agent = create_research_agent()

    research_question = """
Research the current state of AI agent technology.

Explain:

1. What AI agents are
2. How AI agents work
3. What tools AI agents can use
4. How AI agents are different from traditional chatbots
5. Real-world applications of AI agents
6. Important challenges of AI agents

Use web research and provide sources.
"""

    logger.info("Starting web research")

    response = agent.run(research_question)

    print("\n========== DEEP RESEARCH REPORT ==========\n")

    print(response.content)

    logger.info("Deep Research exercise completed successfully")


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()