import logging

from ddgs import DDGS

from agno.agent import Agent
from agno.models.ollama import Ollama


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_multi_source_research")


# ---------------------------------------------------------
# Web Search
# ---------------------------------------------------------

def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Search the web and return structured search results."""

    logger.info("Searching web for: %s", query)

    results = []

    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(
                query,
                max_results=max_results,
            )

            for result in search_results:
                results.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", ""),
                    }
                )

        logger.info(
            "Found %d results for query: %s",
            len(results),
            query,
        )

    except Exception:
        logger.exception(
            "Web search failed for query: %s",
            query,
        )

    return results


# ---------------------------------------------------------
# Multi-source research
# ---------------------------------------------------------

def conduct_research() -> list[dict]:
    """Conduct research using multiple independent searches."""

    logger.info("Starting multi-source research")

    queries = [
        "AI agents definition how they work",
        "AI agents tools real world applications",
        "AI agents challenges safety reliability",
    ]

    all_results = []

    for query in queries:

        results = search_web(
            query=query,
            max_results=5,
        )

        for result in results:
            result["search_query"] = query

        all_results.extend(results)

    logger.info(
        "Collected %d total search results",
        len(all_results),
    )

    return all_results


# ---------------------------------------------------------
# Format research evidence
# ---------------------------------------------------------

def format_research_evidence(
    results: list[dict],
) -> str:
    """Convert search results into evidence for the agent."""

    logger.info("Formatting research evidence")

    if not results:
        logger.warning("No research results available")
        return "No web research results were found."

    evidence = []

    for index, result in enumerate(results, start=1):

        evidence.append(
            f"""
SOURCE {index}
Search Query: {result["search_query"]}
Title: {result["title"]}
URL: {result["url"]}
Summary: {result["snippet"]}
"""
        )

    return "\n".join(evidence)


# ---------------------------------------------------------
# Create Agno research analyst
# ---------------------------------------------------------

def create_research_agent() -> Agent:
    """Create an Agno agent that analyzes collected research."""

    logger.info("Creating research analysis agent")

    agent = Agent(
        model=Ollama(id="llama3.2"),
        instructions=[
            "You are a research analyst.",
            "Analyze only the research evidence provided to you.",
            "Do not claim that you personally searched the web.",
            "Do not invent sources.",
            "Do not invent URLs.",
            "Distinguish evidence from interpretation.",
            "If sources disagree, mention the disagreement.",
            "Provide a clear and concise research report.",
            "Include the source URLs that were provided.",
        ],
        markdown=True,
    )

    logger.info(
        "Research analysis agent created successfully"
    )

    return agent


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    logger.info(
        "Starting Multi-Source Deep Research exercise"
    )

    # -----------------------------------------------------
    # Step 1: Conduct web research
    # -----------------------------------------------------

    research_results = conduct_research()

    # -----------------------------------------------------
    # Step 2: Prepare evidence
    # -----------------------------------------------------

    research_evidence = format_research_evidence(
        research_results
    )

    print("\n========== RESEARCH SOURCES ==========\n")

    for index, result in enumerate(
        research_results,
        start=1,
    ):
        print(f"{index}. {result['title']}")
        print(f"   {result['url']}")
        print()

    # -----------------------------------------------------
    # Step 3: Create Agno analyst
    # -----------------------------------------------------

    agent = create_research_agent()

    # -----------------------------------------------------
    # Step 4: Analyze research
    # -----------------------------------------------------

    prompt = f"""
You are given web research collected from multiple searches.

Research evidence:

{research_evidence}

Create a research report about AI agent technology.

Cover:

1. What AI agents are
2. How AI agents work
3. What tools AI agents can use
4. Difference between AI agents and traditional chatbots
5. Real-world applications
6. Important challenges
7. Key conclusion

Important rules:

- Use only the supplied research evidence.
- Do not invent facts.
- Do not invent sources.
- Do not claim you performed web searches.
- Include relevant source URLs from the evidence.
- If the evidence is insufficient for a claim, say so.
"""

    logger.info(
        "Sending collected research to Agno analyst"
    )

    response = agent.run(prompt)

    print("\n========== MULTI-SOURCE RESEARCH REPORT ==========\n")

    print(response.content)

    logger.info(
        "Multi-Source Deep Research exercise completed successfully"
    )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()