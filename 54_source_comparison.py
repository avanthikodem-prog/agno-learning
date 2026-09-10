"""
Exercise 54 - Source Comparison & Evidence Validation

Architecture:

Research Question
        ↓
Multiple Web Searches
        ↓
Collect Sources
        ↓
Remove Duplicate URLs
        ↓
Extract Evidence
        ↓
Agno + Ollama
        ↓
Compare Sources
        ↓
Validate Evidence
        ↓
Research Conclusion
"""

import logging

from ddgs import DDGS
from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================
# 1. LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_source_comparison")


# ============================================================
# 2. WEB SEARCH
# ============================================================

def search_web(query: str, max_results: int = 5) -> list[dict]:
    """Search the web and return structured results."""

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
            "Search completed: %s | Results: %d",
            query,
            len(results),
        )

    except Exception as exc:
        logger.error(
            "Search failed for '%s': %s",
            query,
            exc,
        )

    return results


# ============================================================
# 3. COLLECT MULTIPLE SOURCES
# ============================================================

def collect_sources() -> list[dict]:
    """Collect sources from multiple research queries."""

    logger.info("Starting multi-source collection.")

    queries = [
        "AI agents agriculture farmer advisory",
        "AI agents agriculture crop monitoring decision support",
        "AI agents agriculture risks reliability limitations",
    ]

    all_sources = []

    for query in queries:
        results = search_web(
            query=query,
            max_results=5,
        )

        all_sources.extend(results)

    logger.info(
        "Raw sources collected: %d",
        len(all_sources),
    )

    return all_sources


# ============================================================
# 4. DEDUPLICATE SOURCES
# ============================================================

def deduplicate_sources(sources: list[dict]) -> list[dict]:
    """Remove duplicate sources using URLs."""

    logger.info(
        "Starting deduplication. Input: %d sources",
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
# 5. BUILD SOURCE EVIDENCE
# ============================================================

def build_evidence(sources: list[dict]) -> str:
    """Convert sources into evidence for the research agent."""

    logger.info(
        "Building evidence from %d sources.",
        len(sources),
    )

    evidence = []

    for index, source in enumerate(sources, start=1):

        title = source.get(
            "title",
            "Unknown title",
        )

        url = source.get(
            "url",
            "Unknown URL",
        )

        snippet = source.get(
            "snippet",
            "No evidence available",
        )

        evidence.append(
            f"""
SOURCE {index}

Title:
{title}

URL:
{url}

Evidence:
{snippet}

----------------------------------------
"""
        )

    combined_evidence = "\n".join(evidence)

    logger.info(
        "Evidence prepared. Characters: %d",
        len(combined_evidence),
    )

    return combined_evidence


# ============================================================
# 6. CREATE AGNO RESEARCH AGENT
# ============================================================

def create_agent() -> Agent:
    """Create the Agno + Ollama research agent."""

    logger.info("Creating source comparison agent.")

    agent = Agent(
        model=Ollama(id="llama3.2"),

        instructions=[
            "You are an evidence validation and source comparison assistant.",
            "Use only the supplied research evidence.",
            "Never invent facts.",
            "Never invent URLs.",
            "Never invent statistics.",
            "Compare information across sources.",
            "Clearly identify agreement and disagreement.",
            "Do not assume that multiple sources automatically make a claim true.",
            "Distinguish evidence from interpretation.",
            "If evidence is insufficient, explicitly say so.",
        ],

        markdown=True,
    )

    logger.info(
        "Source comparison agent created successfully."
    )

    return agent


# ============================================================
# 7. COMPARE AND VALIDATE SOURCES
# ============================================================

def analyze_sources(
    research_question: str,
    sources: list[dict],
) -> str:
    """Compare sources and generate a validated research analysis."""

    logger.info(
        "Starting source comparison and evidence validation."
    )

    evidence = build_evidence(sources)

    agent = create_agent()

    prompt = f"""
Research Question:

{research_question}


Analyze the research evidence below.

Create the following report:


# Source Comparison & Evidence Validation Report

## 1. Research Question

State the research question clearly.


## 2. Source Overview

Briefly explain:

- How many sources were analyzed
- What types of information they provide
- Whether the sources appear to cover different aspects of the topic


## 3. Areas of Agreement

Identify claims or ideas that multiple sources support.

For each important point:

- State the finding
- Mention the supporting source numbers


## 4. Areas of Difference

Identify claims where sources provide different perspectives.

Explain the difference carefully.

Do not create disagreements that are not present in the evidence.


## 5. Evidence Strength

Classify important findings as:

- Strong evidence
- Moderate evidence
- Limited evidence
- Insufficient evidence

Explain why.


## 6. Opportunities

Based only on the evidence, identify realistic opportunities.


## 7. Risks and Limitations

Identify risks, limitations, reliability concerns,
or missing information.


## 8. Evidence-Based Conclusion

Give a balanced conclusion.

Do not make unsupported claims.


## 9. Sources

List the analyzed sources with:

- Source number
- Title
- Exact URL


IMPORTANT RULES:

1. Use ONLY the supplied evidence.
2. Never invent information.
3. Never invent URLs.
4. Never invent statistics.
5. Do not treat search snippets as complete articles.
6. If evidence is weak, say so.
7. If sources agree, identify the agreement.
8. If sources disagree, identify the disagreement.
9. Do not confuse popularity of a claim with evidence quality.
10. Clearly separate facts from interpretation.


RESEARCH QUESTION:

{research_question}


COLLECTED RESEARCH EVIDENCE:

{evidence}
"""

    try:

        logger.info(
            "Sending evidence to Ollama for comparison."
        )

        response = agent.run(prompt)

        report = response.content

        logger.info(
            "Source comparison completed. Report characters: %d",
            len(report),
        )

        return report

    except Exception as exc:

        logger.exception(
            "Source comparison failed: %s",
            exc,
        )

        return "Source comparison failed."


# ============================================================
# 8. MAIN
# ============================================================

def main() -> None:
    """Application entry point."""

    logger.info(
        "Starting Exercise 54 - Source Comparison & Evidence Validation."
    )

    research_question = (
        "How can AI agents be used in agriculture and farmer services, "
        "and what evidence supports their benefits and challenges?"
    )

    logger.info(
        "Research question: %s",
        research_question,
    )

    # --------------------------------------------------------
    # Collect sources
    # --------------------------------------------------------

    raw_sources = collect_sources()

    if not raw_sources:

        logger.error(
            "No sources were collected."
        )

        print("\nNo research sources were collected.")
        print("Please check the internet connection and try again.")

        return

    # --------------------------------------------------------
    # Deduplicate
    # --------------------------------------------------------

    sources = deduplicate_sources(raw_sources)

    # --------------------------------------------------------
    # Limit sources
    # --------------------------------------------------------

    sources = sources[:10]

    logger.info(
        "Final sources selected: %d",
        len(sources),
    )

    # --------------------------------------------------------
    # Analyze
    # --------------------------------------------------------

    report = analyze_sources(
        research_question=research_question,
        sources=sources,
    )

    # --------------------------------------------------------
    # Display report
    # --------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("GRAM SWARAM - SOURCE COMPARISON & EVIDENCE VALIDATION")
    print("=" * 80)

    print(report)

    # --------------------------------------------------------
    # Source list
    # --------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("ANALYZED SOURCES")
    print("=" * 80)

    for index, source in enumerate(sources, start=1):

        print(f"\n[{index}] {source['title']}")
        print(source["url"])

    logger.info(
        "Exercise 54 completed successfully."
    )


# ============================================================
# 9. RUN
# ============================================================

if __name__ == "__main__":
    main()