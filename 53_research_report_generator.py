"""
Exercise 53 - Research Report Generator

Architecture:
Research Questions
        ↓
Multiple Web Searches
        ↓
Collect Sources
        ↓
Remove Duplicate URLs
        ↓
Build Evidence
        ↓
Agno + Ollama
        ↓
Structured Research Report
"""

import logging
from ddgs import DDGS

from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================
# 1. LOGGING CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_research_report")


# ============================================================
# 2. WEB SEARCH FUNCTION
# ============================================================

def search_web(query: str, max_results: int = 5) -> list[dict]:
    """
    Search the web using DDGS.

    Returns a list of search results.
    """

    logger.info("Starting web search: %s", query)

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
            "Search completed: %s | Results found: %d",
            query,
            len(results),
        )

    except Exception as exc:
        logger.error(
            "Search failed for query '%s': %s",
            query,
            exc,
        )

    return results


# ============================================================
# 3. REMOVE DUPLICATE SOURCES
# ============================================================

def deduplicate_sources(sources: list[dict]) -> list[dict]:
    """
    Remove duplicate sources based on URL.
    """

    logger.info(
        "Starting source deduplication. Input sources: %d",
        len(sources),
    )

    unique_sources = []
    seen_urls = set()

    for source in sources:
        url = source.get("url", "").strip()

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)
        unique_sources.append(source)

    logger.info(
        "Deduplication completed. Unique sources: %d",
        len(unique_sources),
    )

    return unique_sources


# ============================================================
# 4. CONDUCT MULTI-SOURCE RESEARCH
# ============================================================

def conduct_research() -> list[dict]:
    """
    Perform research using multiple related search queries.
    """

    logger.info("Starting multi-source research.")

    queries = [
        "AI agents agriculture farmer services",
        "AI agents agriculture crop advisory use cases",
        "AI agents agriculture challenges reliability safety",
    ]

    all_sources = []

    for query in queries:
        results = search_web(
            query=query,
            max_results=5,
        )

        all_sources.extend(results)

    logger.info(
        "Research collection completed. Total raw sources: %d",
        len(all_sources),
    )

    unique_sources = deduplicate_sources(all_sources)

    return unique_sources


# ============================================================
# 5. BUILD EVIDENCE FOR THE AI AGENT
# ============================================================

def build_evidence(sources: list[dict]) -> str:
    """
    Convert collected web sources into structured evidence
    that can be given to the Agno agent.
    """

    logger.info(
        "Building evidence from %d sources.",
        len(sources),
    )

    evidence_parts = []

    for index, source in enumerate(sources, start=1):
        title = source.get("title", "Unknown title")
        url = source.get("url", "Unknown URL")
        snippet = source.get("snippet", "No snippet available")

        evidence_parts.append(
            f"""
SOURCE {index}

Title:
{title}

URL:
{url}

Search Evidence:
{snippet}
"""
        )

    evidence = "\n".join(evidence_parts)

    logger.info(
        "Evidence preparation completed. Characters: %d",
        len(evidence),
    )

    return evidence


# ============================================================
# 6. CREATE RESEARCH AGENT
# ============================================================

def create_research_agent() -> Agent:
    """
    Create the Agno research report generation agent.
    """

    logger.info("Creating Agno research report agent.")

    agent = Agent(
        model=Ollama(id="llama3.2"),

        instructions=[
            "You are a research report generation assistant.",
            "Use ONLY the evidence provided to you.",
            "Do not invent sources, facts, statistics, URLs, or citations.",
            "Clearly separate evidence from interpretation.",
            "If the evidence is insufficient, explicitly say so.",
            "Write in clear and simple professional English.",
            "Create a structured research report.",
        ],

        markdown=True,
    )

    logger.info("Agno research agent created successfully.")

    return agent


# ============================================================
# 7. GENERATE RESEARCH REPORT
# ============================================================

def generate_report(
    research_question: str,
    sources: list[dict],
) -> str:
    """
    Generate the final research report using Agno + Ollama.
    """

    logger.info("Starting research report generation.")

    evidence = build_evidence(sources)

    agent = create_research_agent()

    prompt = f"""
Research Question:

{research_question}


Your task is to create a structured research report using
ONLY the evidence supplied below.


RESEARCH REPORT FORMAT

# Research Report

## 1. Research Question

Clearly state the research question.

## 2. Executive Summary

Give a short summary of the most important findings.

## 3. Key Findings

Provide the major findings as numbered points.

## 4. Evidence Analysis

Explain what the collected sources indicate.

For important claims, mention the source number.

Example:

According to Source 2, ...

## 5. Opportunities

Explain realistic opportunities identified from the evidence.

## 6. Challenges and Risks

Explain limitations, reliability concerns, safety concerns,
or other risks found in the evidence.

## 7. Conclusion

Give a balanced conclusion based only on the evidence.

## 8. Sources

List every source with:

- Source number
- Title
- Exact URL


IMPORTANT RULES

1. Do not invent information.
2. Do not create fake URLs.
3. Do not claim a source says something unless its evidence supports it.
4. If evidence conflicts between sources, mention the conflict.
5. If there is insufficient evidence, say "Insufficient evidence."
6. Do not add unsupported statistics.
7. Keep the report understandable to a beginner.


RESEARCH QUESTION

{research_question}


COLLECTED EVIDENCE

{evidence}
"""

    logger.info("Sending research evidence to Ollama.")

    try:
        response = agent.run(prompt)

        report = response.content

        logger.info(
            "Research report generated successfully. Characters: %d",
            len(report),
        )

        return report

    except Exception as exc:
        logger.exception(
            "Research report generation failed: %s",
            exc,
        )

        return "Research report generation failed."


# ============================================================
# 8. MAIN PROGRAM
# ============================================================

def main() -> None:
    """
    Main application entry point.
    """

    logger.info("Starting Exercise 53 - Research Report Generator.")

    research_question = (
        "How can AI agents be used in agriculture and farmer services, "
        "and what are the major opportunities and challenges?"
    )

    logger.info(
        "Research question: %s",
        research_question,
    )

    # --------------------------------------------------------
    # Step 1: Collect research sources
    # --------------------------------------------------------

    sources = conduct_research()

    if not sources:
        logger.error(
            "No research sources were collected."
        )

        print("\nNo research sources were available.")
        print("Please check the web search connection and try again.")

        return

    # --------------------------------------------------------
    # Step 2: Limit the number of sources
    # --------------------------------------------------------

    sources = sources[:10]

    logger.info(
        "Using %d sources for final report.",
        len(sources),
    )

    # --------------------------------------------------------
    # Step 3: Generate report
    # --------------------------------------------------------

    report = generate_report(
        research_question=research_question,
        sources=sources,
    )

    # --------------------------------------------------------
    # Step 4: Display report
    # --------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("GRAM SWARAM - RESEARCH REPORT")
    print("=" * 80)

    print(report)

    print("\n")
    print("=" * 80)
    print("SOURCE LIST")
    print("=" * 80)

    for index, source in enumerate(sources, start=1):
        print(f"\n[{index}] {source['title']}")
        print(source["url"])

    logger.info(
        "Exercise 53 completed successfully."
    )


# ============================================================
# 9. RUN PROGRAM
# ============================================================

if __name__ == "__main__":
    main()