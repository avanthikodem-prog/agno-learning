"""
Exercise 56.1 - Robust Dynamic Research Retrieval

Goal:
Improve Exercise 56 by making the research retrieval layer
more reliable.

Architecture:

Research Question
        ↓
AI-generated Search Queries
        ↓
Query Cleaning
        ↓
DDGS Search
        ↓
Retry / Simplified Query
        ↓
Source Filtering
        ↓
Deduplication
        ↓
Evidence
        ↓
Agno + Ollama
        ↓
Final Research Report
"""

import logging
import re
from typing import List, Dict
from urllib.parse import urlparse

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

logger = logging.getLogger("gram_swaram_robust_research")


# ============================================================
# Configuration
# ============================================================

MODEL_NAME = "llama3.2"

MAX_SEARCH_QUERIES = 6
RESULTS_PER_QUERY = 5
MAX_FINAL_SOURCES = 12

MINIMUM_SOURCES_REQUIRED = 5

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

    logger.info(
        "Creating Agno agent with Ollama model: %s",
        MODEL_NAME,
    )

    return Agent(
        model=Ollama(id=MODEL_NAME),
        instructions=instructions,
        markdown=False,
    )


# ============================================================
# Generate Search Queries
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
            "Do not use quotation marks around queries.",
            "Avoid duplicate queries.",
        ]
    )

    prompt = f"""
Research Question:

{question}

Generate exactly 6 useful web search queries.

The queries must cover different research angles.

Return ONLY this format:

SEARCH_QUERIES:
1. query one
2. query two
3. query three
4. query four
5. query five
6. query six

Do not add explanations.
Do not put quotation marks around the queries.
"""

    try:

        response = planner.run(prompt)

        raw_output = response.content or ""

        logger.info(
            "Research planner response received: %d characters",
            len(raw_output),
        )

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

        # Remove quotation marks if the model still adds them
        cleaned_queries = []

        for query in queries:

            query = query.strip()

            query = query.strip('"')
            query = query.strip("'")

            query = re.sub(
                r"\s+",
                " ",
                query,
            )

            if query:
                cleaned_queries.append(query)

        # Remove duplicates
        unique_queries = []

        seen = set()

        for query in cleaned_queries:

            normalized = query.lower()

            if normalized not in seen:

                seen.add(normalized)
                unique_queries.append(query)

        queries = unique_queries[:MAX_SEARCH_QUERIES]

        if queries:

            logger.info(
                "Successfully extracted %d dynamic search queries",
                len(queries),
            )

            for index, query in enumerate(
                queries,
                start=1,
            ):
                logger.info(
                    "Generated Query %d: %s",
                    index,
                    query,
                )

            return queries

        logger.warning(
            "Could not extract search queries from planner output."
        )

    except Exception as exc:

        logger.exception(
            "Research planner failed: %s",
            exc,
        )

    # --------------------------------------------------------
    # Fallback queries
    # --------------------------------------------------------

    logger.warning(
        "Using fallback search queries."
    )

    return [
        "AI agriculture India farmers",
        "voice AI farmers India agriculture",
        "AI crop advisory India farmers",
        "agricultural extension services AI India",
        "voice technology rural farmers India",
        "AI agriculture benefits challenges India",
    ]


# ============================================================
# Clean Search Query
# ============================================================

def clean_search_query(query: str) -> str:
    """
    Clean a search query before sending it to DDGS.
    """

    cleaned = query.strip()

    # Remove quotation marks
    cleaned = cleaned.replace('"', "")
    cleaned = cleaned.replace("'", "")

    # Remove unnecessary punctuation
    cleaned = re.sub(
        r"[{}[\]()]",
        " ",
        cleaned,
    )

    # Replace multiple spaces
    cleaned = re.sub(
        r"\s+",
        " ",
        cleaned,
    )

    cleaned = cleaned.strip()

    logger.info(
        "Cleaned query: %s",
        cleaned,
    )

    return cleaned


# ============================================================
# Validate URL
# ============================================================

def is_valid_url(url: str) -> bool:
    """
    Check whether a URL is valid and suitable as a research source.
    """

    if not url:
        return False

    try:

        parsed = urlparse(url)

        if parsed.scheme not in (
            "http",
            "https",
        ):
            return False

        if not parsed.netloc:
            return False

        # Reject obvious advertising/click-tracking URLs
        blocked_patterns = [
            "aclick",
            "ad.doubleclick",
            "googleadservices",
            "bing.com/aclick",
        ]

        url_lower = url.lower()

        for pattern in blocked_patterns:

            if pattern in url_lower:

                logger.debug(
                    "Rejected advertising URL: %s",
                    url,
                )

                return False

        return True

    except Exception:

        return False


# ============================================================
# Search Web
# ============================================================

def search_web(
    query: str,
    retry: bool = True,
) -> List[Dict]:
    """
    Search the web using DDGS.

    If the original search fails or returns nothing,
    retry using a simplified query.
    """

    cleaned_query = clean_search_query(query)

    logger.info(
        "Searching web: %s",
        cleaned_query,
    )

    results = []

    try:

        with DDGS() as ddgs:

            search_results = ddgs.text(
                cleaned_query,
                max_results=RESULTS_PER_QUERY,
            )

            for result in search_results:

                title = result.get(
                    "title",
                    "",
                )

                url = result.get(
                    "href",
                    "",
                )

                snippet = result.get(
                    "body",
                    "",
                )

                if not is_valid_url(url):

                    logger.debug(
                        "Skipping invalid URL: %s",
                        url,
                    )

                    continue

                results.append(
                    {
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                        "query": cleaned_query,
                    }
                )

        logger.info(
            "Search returned %d usable results",
            len(results),
        )

    except Exception as exc:

        logger.warning(
            "Search failed: %s",
            exc,
        )

    # ========================================================
    # Retry with simplified query
    # ========================================================

    if not results and retry:

        words = cleaned_query.split()

        # Keep the important keywords
        simplified_query = " ".join(
            words[:8]
        )

        if simplified_query != cleaned_query:

            logger.warning(
                "Retrying with simplified query: %s",
                simplified_query,
            )

            return search_web(
                simplified_query,
                retry=False,
            )

        logger.warning(
            "No results and no simpler retry available."
        )

    return results


# ============================================================
# Execute Dynamic Searches
# ============================================================

def execute_dynamic_searches(
    queries: List[str],
) -> List[Dict]:
    """
    Execute all generated queries.
    """

    logger.info(
        "Starting robust dynamic web research with %d queries",
        len(queries),
    )

    all_sources = []

    for index, query in enumerate(
        queries,
        start=1,
    ):

        logger.info(
            "Executing query %d/%d",
            index,
            len(queries),
        )

        results = search_web(query)

        if results:

            all_sources.extend(results)

        else:

            logger.warning(
                "No usable sources found for query %d",
                index,
            )

    logger.info(
        "Dynamic search completed. Raw sources: %d",
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

    logger.info(
        "Starting source deduplication..."
    )

    seen_urls = set()

    unique_sources = []

    for source in sources:

        url = source.get(
            "url",
            "",
        ).strip()

        if not url:
            continue

        # Normalize URL
        normalized_url = url.rstrip("/").lower()

        if normalized_url in seen_urls:

            logger.debug(
                "Duplicate source skipped: %s",
                url,
            )

            continue

        seen_urls.add(normalized_url)

        unique_sources.append(source)

    logger.info(
        "Unique sources: %d",
        len(unique_sources),
    )

    final_sources = unique_sources[
        :MAX_FINAL_SOURCES
    ]

    logger.info(
        "Final sources selected: %d",
        len(final_sources),
    )

    return final_sources


# ============================================================
# Check Source Quality
# ============================================================

def check_source_quality(
    sources: List[Dict],
) -> None:
    """
    Log a basic source-quality assessment.

    This is not scientific verification.
    It only checks whether enough usable sources were collected.
    """

    source_count = len(sources)

    logger.info(
        "Checking research source quality..."
    )

    if source_count >= MINIMUM_SOURCES_REQUIRED:

        logger.info(
            "Source quality check PASSED: %d sources available",
            source_count,
        )

    else:

        logger.warning(
            "Source quality check WARNING: only %d sources available; "
            "minimum recommended is %d",
            source_count,
            MINIMUM_SOURCES_REQUIRED,
        )


# ============================================================
# Build Evidence
# ============================================================

def build_evidence(
    sources: List[Dict],
) -> str:
    """
    Convert sources into evidence text.
    """

    logger.info(
        "Building research evidence..."
    )

    evidence_parts = []

    for index, source in enumerate(
        sources,
        start=1,
    ):

        evidence_parts.append(
            f"""
SOURCE {index}

Search Query:
{source.get("query", "")}

Title:
{source.get("title", "")}

URL:
{source.get("url", "")}

Evidence:
{source.get("snippet", "")}
"""
        )

    evidence = "\n".join(
        evidence_parts
    )

    logger.info(
        "Evidence prepared: %d characters",
        len(evidence),
    )

    return evidence


# ============================================================
# Generate Final Report
# ============================================================

def generate_final_report(
    question: str,
    queries: List[str],
    sources: List[Dict],
    evidence: str,
) -> str:
    """
    Generate the final research report using Agno + Ollama.
    """

    logger.info(
        "Starting final research synthesis..."
    )

    researcher = create_agent(
        instructions=[
            "You are an evidence-based research analyst.",
            "Use only the supplied research evidence.",
            "Do not invent statistics.",
            "Do not invent sources.",
            "Do not treat unsupported claims as facts.",
            "Clearly mention evidence limitations.",
            "Distinguish search snippets from verified evidence.",
        ]
    )

    query_text = "\n".join(
        f"{index}. {query}"
        for index, query in enumerate(
            queries,
            start=1,
        )
    )

    source_text = "\n".join(
        f"{index}. {source.get('title', '')} - "
        f"{source.get('url', '')}"
        for index, source in enumerate(
            sources,
            start=1,
        )
    )

    prompt = f"""
Research Question:

{question}


DYNAMIC SEARCH QUERIES:

{query_text}


COLLECTED SOURCES:

{source_text}


RESEARCH EVIDENCE:

{evidence}


Create an evidence-based research report.

Use these sections:

1. Research Question

2. Executive Summary

3. Dynamic Search Strategy

4. Key Findings

5. Evidence Analysis

6. Opportunities

7. Challenges and Risks

8. Evidence Gaps

9. Source Quality Assessment

10. Conclusion

11. Sources

Important rules:

- Use only the supplied evidence.
- Do not invent facts.
- Do not invent statistics.
- Do not invent citations.
- If the evidence is weak, explicitly say that it is weak.
- If there are conflicting findings, mention them.
- Do not treat search-result snippets as fully verified research papers.
- Clearly distinguish evidence from reasonable interpretation.
"""

    try:

        response = researcher.run(
            prompt
        )

        report = response.content or ""

        logger.info(
            "Final research report generated: %d characters",
            len(report),
        )

        return report

    except Exception as exc:

        logger.exception(
            "Final research synthesis failed: %s",
            exc,
        )

        return (
            "Final research report generation failed.\n"
            f"Error: {exc}"
        )


# ============================================================
# Main
# ============================================================

def main():

    logger.info("=" * 70)
    logger.info(
        "Starting Robust Dynamic Research Agent"
    )
    logger.info("=" * 70)

    logger.info(
        "Research Question: %s",
        RESEARCH_QUESTION,
    )

    # --------------------------------------------------------
    # STEP 1
    # Generate dynamic queries
    # --------------------------------------------------------

    queries = generate_search_queries(
        RESEARCH_QUESTION
    )

    print("\n" + "=" * 70)
    print("DYNAMIC SEARCH QUERIES")
    print("=" * 70)

    for index, query in enumerate(
        queries,
        start=1,
    ):
        print(
            f"{index}. {query}"
        )

    # --------------------------------------------------------
    # STEP 2
    # Execute searches
    # --------------------------------------------------------

    raw_sources = execute_dynamic_searches(
        queries
    )

    # --------------------------------------------------------
    # STEP 3
    # Deduplicate
    # --------------------------------------------------------

    sources = deduplicate_sources(
        raw_sources
    )

    # --------------------------------------------------------
    # STEP 4
    # Check quality
    # --------------------------------------------------------

    check_source_quality(
        sources
    )

    # --------------------------------------------------------
    # STEP 5
    # Build evidence
    # --------------------------------------------------------

    evidence = build_evidence(
        sources
    )

    # --------------------------------------------------------
    # STEP 6
    # Generate report
    # --------------------------------------------------------

    report = generate_final_report(
        question=RESEARCH_QUESTION,
        queries=queries,
        sources=sources,
        evidence=evidence,
    )

    # --------------------------------------------------------
    # Display report
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("FINAL ROBUST DYNAMIC RESEARCH REPORT")
    print("=" * 70)

    print(report)

    logger.info("=" * 70)
    logger.info(
        "Robust Dynamic Research Agent completed"
    )
    logger.info("=" * 70)


# ============================================================
# Entry Point
# ============================================================

if __name__ == "__main__":
    main()