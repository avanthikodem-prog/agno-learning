"""
Exercise 56 - Dynamic Research Agent

Architecture:

Research Question
        ↓
AI Research Planner
        ↓
AI-generated Search Queries
        ↓
Python extracts queries
        ↓
DDGS Web Search
        ↓
Source Collection
        ↓
Deduplication
        ↓
Evidence Preparation
        ↓
Agno + Ollama
        ↓
Final Research Report
"""

import logging
import re
from typing import List, Dict

from ddgs import DDGS
from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================
# Logging Configuration
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_dynamic_research")


# ============================================================
# Configuration
# ============================================================

MODEL_NAME = "llama3.2"

MAX_SEARCH_QUERIES = 6
RESULTS_PER_QUERY = 4
MAX_FINAL_SOURCES = 12

RESEARCH_QUESTION = (
    "How can AI agents improve farmer services in India, "
    "especially through voice-based agricultural assistance?"
)


# ============================================================
# Create Agno Agent
# ============================================================

def create_agent(instructions: List[str]) -> Agent:
    """
    Create an Agno agent using the local Ollama model.
    """

    logger.info("Creating Agno agent with Ollama model: %s", MODEL_NAME)

    return Agent(
        model=Ollama(id=MODEL_NAME),
        instructions=instructions,
        markdown=False,
    )


# ============================================================
# Generate Dynamic Search Queries
# ============================================================

def generate_search_queries(question: str) -> List[str]:
    """
    Ask the LLM to generate research-specific search queries.
    """

    logger.info("Generating dynamic search queries...")

    planner = create_agent(
        instructions=[
            "You are an expert research planning assistant.",
            "Generate high-quality web search queries.",
            "Queries must directly help answer the research question.",
            "Cover different perspectives such as technology, agriculture, "
            "farmer adoption, voice AI, benefits, risks, and real-world examples.",
            "Avoid duplicate or nearly identical queries.",
        ]
    )

    prompt = f"""
Research Question:

{question}

Generate exactly 6 useful web search queries.

Return ONLY this format:

SEARCH_QUERIES:
1. query one
2. query two
3. query three
4. query four
5. query five
6. query six

Do not add explanations before or after the list.
"""

    try:
        response = planner.run(prompt)

        raw_output = response.content or ""

        logger.info(
            "Research planner response received: %d characters",
            len(raw_output),
        )

        logger.debug("Planner raw output:\n%s", raw_output)

        queries = []

        search_section = False

        for line in raw_output.splitlines():

            line = line.strip()

            if line.upper().startswith("SEARCH_QUERIES"):
                search_section = True
                continue

            if not search_section:
                continue

            match = re.match(
                r"^\d+\s*[\.\)\:\-]\s*(.+)$",
                line,
            )

            if match:
                query = match.group(1).strip()

                if query:
                    queries.append(query)

        # Remove duplicate queries while preserving order
        unique_queries = []

        for query in queries:
            normalized = query.lower()

            if normalized not in [
                existing.lower()
                for existing in unique_queries
            ]:
                unique_queries.append(query)

        queries = unique_queries[:MAX_SEARCH_QUERIES]

        if queries:
            logger.info(
                "Successfully extracted %d dynamic search queries",
                len(queries),
            )

            for index, query in enumerate(queries, start=1):
                logger.info(
                    "Generated Query %d: %s",
                    index,
                    query,
                )

            return queries

        logger.warning(
            "Could not parse search queries from planner output."
        )

    except Exception as exc:
        logger.exception(
            "Research planner failed: %s",
            exc,
        )

    # --------------------------------------------------------
    # Fallback queries
    # --------------------------------------------------------

    logger.warning("Using fallback search queries.")

    fallback_queries = [
        "AI agents agriculture India farmer services",
        "voice AI agricultural assistance farmers India",
        "AI precision agriculture India farmers",
        "AI crop advisory systems India",
        "voice technology rural farmers India",
        "AI agriculture benefits challenges India",
    ]

    return fallback_queries[:MAX_SEARCH_QUERIES]


# ============================================================
# Search One Query
# ============================================================

def search_web(query: str) -> List[Dict]:
    """
    Search the web using DDGS.
    """

    logger.info("Searching web for: %s", query)

    results = []

    try:
        with DDGS() as ddgs:

            search_results = ddgs.text(
                query,
                max_results=RESULTS_PER_QUERY,
            )

            for result in search_results:

                results.append(
                    {
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "snippet": result.get("body", ""),
                        "query": query,
                    }
                )

        logger.info(
            "Search completed: %d results for query",
            len(results),
        )

    except Exception as exc:

        logger.warning(
            "Search failed for query '%s': %s",
            query,
            exc,
        )

    return results


# ============================================================
# Execute Dynamic Searches
# ============================================================

def execute_dynamic_searches(
    queries: List[str],
) -> List[Dict]:
    """
    Execute all AI-generated search queries.
    """

    logger.info(
        "Starting dynamic web research with %d queries",
        len(queries),
    )

    all_sources = []

    for index, query in enumerate(queries, start=1):

        logger.info(
            "Executing generated query %d/%d",
            index,
            len(queries),
        )

        results = search_web(query)

        all_sources.extend(results)

    logger.info(
        "Dynamic research completed. Raw sources: %d",
        len(all_sources),
    )

    return all_sources


# ============================================================
# Deduplicate Sources
# ============================================================

def deduplicate_sources(
    sources: List[Dict],
) -> List[Dict]:
    """
    Remove duplicate URLs.
    """

    logger.info("Starting source deduplication...")

    seen_urls = set()
    unique_sources = []

    for source in sources:

        url = source.get("url", "").strip()

        if not url:
            continue

        if url in seen_urls:
            continue

        seen_urls.add(url)
        unique_sources.append(source)

    logger.info(
        "Unique sources after deduplication: %d",
        len(unique_sources),
    )

    final_sources = unique_sources[:MAX_FINAL_SOURCES]

    logger.info(
        "Final sources selected for synthesis: %d",
        len(final_sources),
    )

    return final_sources


# ============================================================
# Build Evidence
# ============================================================

def build_evidence(
    sources: List[Dict],
) -> str:
    """
    Convert collected sources into compact evidence text.
    """

    logger.info("Building evidence from collected sources...")

    evidence_parts = []

    for index, source in enumerate(sources, start=1):

        title = source.get("title", "")
        url = source.get("url", "")
        snippet = source.get("snippet", "")
        query = source.get("query", "")

        evidence_parts.append(
            f"""
SOURCE {index}

Search Query:
{query}

Title:
{title}

URL:
{url}

Evidence:
{snippet}
"""
        )

    evidence = "\n".join(evidence_parts)

    logger.info(
        "Evidence prepared: %d characters",
        len(evidence),
    )

    return evidence


# ============================================================
# Generate Final Research Report
# ============================================================

def generate_final_report(
    question: str,
    queries: List[str],
    sources: List[Dict],
    evidence: str,
) -> str:
    """
    Use Agno + Ollama to synthesize the final research report.
    """

    logger.info("Starting final research synthesis...")

    researcher = create_agent(
        instructions=[
            "You are an evidence-based research analyst.",
            "Use only the supplied research evidence.",
            "Do not invent facts or sources.",
            "Clearly distinguish evidence from assumptions.",
            "If evidence is insufficient, say so.",
            "Compare information across sources.",
            "Produce a structured professional research report.",
        ]
    )

    query_text = "\n".join(
        f"{index}. {query}"
        for index, query in enumerate(queries, start=1)
    )

    source_text = "\n".join(
        f"{index}. {source['title']} - {source['url']}"
        for index, source in enumerate(sources, start=1)
    )

    prompt = f"""
Research Question:

{question}


DYNAMIC SEARCH QUERIES USED:

{query_text}


SOURCES COLLECTED:

{source_text}


RESEARCH EVIDENCE:

{evidence}


Prepare a final evidence-based research report.

Use exactly these sections:

1. Research Question

2. Executive Summary

3. Dynamic Search Strategy

4. Key Findings

5. Evidence Analysis

6. Opportunities

7. Challenges and Risks

8. Evidence Gaps

9. Conclusion

10. Sources

Important rules:

- Base factual claims on the supplied evidence.
- Do not invent statistics.
- Do not invent sources.
- Do not claim that a source says something that is not supported
  by its supplied evidence.
- Mention conflicting evidence when present.
- Mention limitations of using search-result snippets.
- Keep the report practical and clear.
"""

    try:

        response = researcher.run(prompt)

        report = response.content or ""

        logger.info(
            "Final research report generated: %d characters",
            len(report),
        )

        return report

    except Exception as exc:

        logger.exception(
            "Final synthesis failed: %s",
            exc,
        )

        return (
            "Final report generation failed.\n"
            f"Error: {exc}"
        )


# ============================================================
# Main
# ============================================================

def main():

    logger.info("=" * 70)
    logger.info("Starting Dynamic Research Agent")
    logger.info("=" * 70)

    logger.info(
        "Research Question: %s",
        RESEARCH_QUESTION,
    )

    # --------------------------------------------------------
    # Step 1: Generate queries dynamically
    # --------------------------------------------------------

    queries = generate_search_queries(
        RESEARCH_QUESTION
    )

    print("\n" + "=" * 70)
    print("DYNAMIC SEARCH QUERIES")
    print("=" * 70)

    for index, query in enumerate(queries, start=1):
        print(f"{index}. {query}")

    # --------------------------------------------------------
    # Step 2: Execute generated searches
    # --------------------------------------------------------

    raw_sources = execute_dynamic_searches(
        queries
    )

    # --------------------------------------------------------
    # Step 3: Deduplicate
    # --------------------------------------------------------

    sources = deduplicate_sources(
        raw_sources
    )

    # --------------------------------------------------------
    # Step 4: Build evidence
    # --------------------------------------------------------

    evidence = build_evidence(
        sources
    )

    # --------------------------------------------------------
    # Step 5: Generate final report
    # --------------------------------------------------------

    report = generate_final_report(
        question=RESEARCH_QUESTION,
        queries=queries,
        sources=sources,
        evidence=evidence,
    )

    # --------------------------------------------------------
    # Display final report
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL DYNAMIC RESEARCH REPORT")
    print("=" * 70)

    print(report)

    logger.info("=" * 70)
    logger.info("Dynamic Research Agent completed successfully")
    logger.info("=" * 70)


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()