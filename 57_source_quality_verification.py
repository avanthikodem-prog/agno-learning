import logging
import re
from urllib.parse import urlparse

from ddgs import DDGS
from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_source_verification")


# ============================================================
# CONFIGURATION
# ============================================================

RESEARCH_QUESTION = (
    "How can AI-powered voice assistants help farmers in rural India?"
)

MAX_RESULTS_PER_QUERY = 5
MAX_FINAL_SOURCES = 8
MINIMUM_SOURCES = 5


# ============================================================
# STEP 1 — RESEARCH PLANNER
# ============================================================

def generate_search_queries(question: str) -> list[str]:
    """
    Ask Agno + Ollama to generate multiple research queries.
    """

    logger.info("Generating research search queries...")

    planner = Agent(
        model=Ollama(id="llama3.2"),
        instructions=[
            "You are a research planning assistant.",
            "Generate 6 high-quality web search queries.",
            "Focus on AI-powered voice assistants and agriculture in India.",
            "Queries must be plain search phrases.",
            "Do not use quotation marks.",
            "Do not number the queries.",
            "Put each query on a separate line.",
        ],
        markdown=False,
    )

    response = planner.run(
        f"""
Research question:

{question}

Generate 6 different search queries covering:
- AI voice assistants for farmers
- agricultural advisory systems
- Indian government initiatives
- farmer adoption
- benefits and limitations
- real-world implementations
"""
    )

    text = response.content.strip()

    queries = []

    for line in text.splitlines():
        line = re.sub(r"^\s*[-*•\d.)]+\s*", "", line).strip()

        if line and len(line) > 10:
            queries.append(line)

    # Remove duplicates
    unique_queries = list(dict.fromkeys(queries))

    logger.info("Generated %d search queries.", len(unique_queries))

    for index, query in enumerate(unique_queries, start=1):
        logger.info("Query %d: %s", index, query)

    return unique_queries[:6]


# ============================================================
# STEP 2 — SEARCH WEB
# ============================================================

def search_web(queries: list[str]) -> list[dict]:
    """
    Search the web using DDGS.
    """

    logger.info("Starting web search...")

    all_sources = []

    with DDGS() as ddgs:

        for query in queries:

            logger.info("Searching: %s", query)

            try:
                results = list(
                    ddgs.text(
                        query,
                        max_results=MAX_RESULTS_PER_QUERY,
                    )
                )

                logger.info(
                    "Found %d results for query.",
                    len(results),
                )

                for result in results:

                    title = result.get("title", "").strip()
                    url = result.get("href", "").strip()
                    snippet = result.get("body", "").strip()

                    if not url:
                        continue

                    all_sources.append(
                        {
                            "title": title,
                            "url": url,
                            "snippet": snippet,
                            "query": query,
                        }
                    )

            except Exception as exc:
                logger.warning(
                    "Search failed for query '%s': %s",
                    query,
                    exc,
                )

    logger.info(
        "Total raw sources collected: %d",
        len(all_sources),
    )

    return all_sources


# ============================================================
# STEP 3 — URL VALIDATION
# ============================================================

def is_valid_url(url: str) -> bool:
    """
    Check whether a URL has a valid HTTP/HTTPS scheme and domain.
    """

    try:
        parsed = urlparse(url)

        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.netloc)
        )

    except Exception:
        return False


# ============================================================
# STEP 4 — DOMAIN EXTRACTION
# ============================================================

def extract_domain(url: str) -> str:
    """
    Extract the domain from a URL.
    """

    try:
        domain = urlparse(url).netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    except Exception:
        return ""


# ============================================================
# STEP 5 — SOURCE TYPE CLASSIFICATION
# ============================================================

def classify_source_type(domain: str) -> str:
    """
    Deterministic first-pass classification.

    Important:
    Domain type alone does NOT prove that a source is trustworthy.
    """

    domain = domain.lower()

    # Government
    if (
        domain.endswith(".gov.in")
        or domain.endswith(".gov")
        or ".gov.in" in domain
    ):
        return "Government / Official"

    # Academic / research
    academic_domains = [
        ".edu",
        ".ac.in",
        "arxiv.org",
        "nature.com",
        "sciencedirect.com",
        "springer.com",
        "ieee.org",
        "scielo.org",
        "pubmed.ncbi.nlm.nih.gov",
        "ncbi.nlm.nih.gov",
        "researchgate.net",
    ]

    if any(domain.endswith(item) or item in domain for item in academic_domains):
        return "Academic / Research"

    # News / media
    news_domains = [
        "reuters.com",
        "bbc.com",
        "bbc.co.uk",
        "thehindu.com",
        "indianexpress.com",
        "hindustantimes.com",
        "timesofindia.indiatimes.com",
        "economictimes.indiatimes.com",
        "techcrunch.com",
    ]

    if any(item in domain for item in news_domains):
        return "News / Industry"

    # Company / commercial
    company_indicators = [
        ".com",
        ".ai",
        ".io",
        ".co",
    ]

    if any(domain.endswith(item) for item in company_indicators):
        return "Company / Commercial"

    return "Other"


# ============================================================
# STEP 6 — DEDUPLICATION
# ============================================================

def deduplicate_sources(sources: list[dict]) -> list[dict]:
    """
    Remove duplicate URLs.
    """

    logger.info("Deduplicating sources...")

    unique = []
    seen_urls = set()

    for source in sources:

        url = source["url"].rstrip("/").lower()

        if url in seen_urls:
            continue

        seen_urls.add(url)
        unique.append(source)

    logger.info(
        "Unique sources after deduplication: %d",
        len(unique),
    )

    return unique


# ============================================================
# STEP 7 — RULE-BASED QUALITY SCORE
# ============================================================

def calculate_rule_score(source_type: str, domain: str) -> int:
    """
    Calculate an initial deterministic source score.

    This is only a preliminary score.
    It is NOT proof of factual accuracy.
    """

    score = 0

    if source_type == "Government / Official":
        score = 10

    elif source_type == "Academic / Research":
        score = 9

    elif source_type == "News / Industry":
        score = 7

    elif source_type == "Company / Commercial":
        score = 5

    else:
        score = 3

    # Additional known scholarly indicators
    scholarly_domains = [
        "doi.org",
        "arxiv.org",
        "nature.com",
        "sciencedirect.com",
        "springer.com",
        "ieee.org",
    ]

    if any(item in domain for item in scholarly_domains):
        score = min(score + 1, 10)

    return score


# ============================================================
# STEP 8 — VERIFY SOURCES
# ============================================================

def verify_sources(sources: list[dict]) -> list[dict]:
    """
    Add deterministic source-quality metadata.
    """

    logger.info("Starting source quality verification...")

    verified_sources = []

    for source in sources:

        url = source["url"]

        if not is_valid_url(url):
            logger.warning(
                "Skipping invalid URL: %s",
                url,
            )
            continue

        domain = extract_domain(url)

        source_type = classify_source_type(domain)

        rule_score = calculate_rule_score(
            source_type,
            domain,
        )

        verified_source = {
            **source,
            "domain": domain,
            "source_type": source_type,
            "rule_score": rule_score,
        }

        verified_sources.append(verified_source)

    # Highest rule score first
    verified_sources.sort(
        key=lambda item: item["rule_score"],
        reverse=True,
    )

    logger.info(
        "Verified %d sources.",
        len(verified_sources),
    )

    return verified_sources


# ============================================================
# STEP 9 — DISPLAY SOURCE QUALITY
# ============================================================

def display_source_quality(sources: list[dict]) -> None:
    """
    Display the deterministic verification results.
    """

    logger.info("========== SOURCE QUALITY RESULTS ==========")

    for index, source in enumerate(sources, start=1):

        logger.info(
            "%d. %s | %s | Score: %d/10",
            index,
            source["source_type"],
            source["domain"],
            source["rule_score"],
        )


# ============================================================
# STEP 10 — PREPARE EVIDENCE
# ============================================================

def prepare_evidence(sources: list[dict]) -> str:
    """
    Prepare verified source information for the final AI report.
    """

    selected_sources = sources[:MAX_FINAL_SOURCES]

    evidence_parts = []

    for index, source in enumerate(selected_sources, start=1):

        evidence_parts.append(
            f"""
SOURCE {index}

Title:
{source["title"]}

URL:
{source["url"]}

Domain:
{source["domain"]}

Source Type:
{source["source_type"]}

Preliminary Rule Score:
{source["rule_score"]}/10

Search Query:
{source["query"]}

Snippet:
{source["snippet"]}
"""
        )

    evidence = "\n".join(evidence_parts)

    logger.info(
        "Prepared evidence from %d sources.",
        len(selected_sources),
    )

    logger.info(
        "Evidence length: %d characters.",
        len(evidence),
    )

    return evidence


# ============================================================
# STEP 11 — FINAL RESEARCH REPORT
# ============================================================

def generate_final_report(
    question: str,
    evidence: str,
) -> str:
    """
    Generate the final research report using Agno + Ollama.
    """

    logger.info("Generating final research report...")

    researcher = Agent(
        model=Ollama(id="llama3.2"),
        instructions=[
            "You are an evidence-based research analyst.",
            "Use ONLY the supplied source evidence.",
            "Do not invent facts, statistics, organizations, or URLs.",
            "Clearly distinguish evidence from interpretation.",
            "Do not treat the preliminary rule score as proof of factual accuracy.",
            "Company sources may contain promotional bias.",
            "Government and academic sources should be treated as stronger starting points,",
            "but their claims should still be evaluated critically.",
            "If evidence is insufficient, explicitly say so.",
            "Do not claim that you opened or verified webpages.",
            "Produce a structured research report.",
        ],
        markdown=False,
    )

    prompt = f"""
Research Question:
{question}

Verified Source Evidence:
{evidence}

Create a research report with these sections:

1. Research Question
2. Executive Summary
3. Search Strategy
4. Verified Source Overview
5. Key Findings
6. Evidence Analysis
7. Opportunities
8. Challenges and Risks
9. Evidence Gaps
10. Source Quality Assessment
11. Conclusion
12. Sources

For Source Quality Assessment:
- explain the different source types
- explain strengths and limitations
- mention that rule-based scores are preliminary
- identify possible promotional bias
- do not claim absolute verification
"""

    response = researcher.run(prompt)

    report = response.content.strip()

    logger.info(
        "Final report generated: %d characters.",
        len(report),
    )

    return report


# ============================================================
# STEP 12 — MAIN PIPELINE
# ============================================================

def main() -> None:

    logger.info("==========================================")
    logger.info("Starting Research Source Verification")
    logger.info("==========================================")

    logger.info(
        "Research question: %s",
        RESEARCH_QUESTION,
    )

    # 1. Generate queries
    queries = generate_search_queries(
        RESEARCH_QUESTION
    )

    if not queries:
        logger.error("No search queries generated.")
        return

    # 2. Search
    raw_sources = search_web(queries)

    if not raw_sources:
        logger.error("No sources were found.")
        return

    # 3. Deduplicate
    unique_sources = deduplicate_sources(
        raw_sources
    )

    # 4. Verify
    verified_sources = verify_sources(
        unique_sources
    )

    # 5. Display quality
    display_source_quality(
        verified_sources
    )

    # 6. Minimum source check
    if len(verified_sources) < MINIMUM_SOURCES:

        logger.warning(
            "Only %d verified sources found. Minimum recommended: %d",
            len(verified_sources),
            MINIMUM_SOURCES,
        )

    else:

        logger.info(
            "Source quality check passed: %d sources available.",
            len(verified_sources),
        )

    # 7. Prepare evidence
    evidence = prepare_evidence(
        verified_sources
    )

    # 8. Generate report
    report = generate_final_report(
        RESEARCH_QUESTION,
        evidence,
    )

    # 9. Print final report
    print("\n")
    print("=" * 70)
    print("FINAL VERIFIED RESEARCH REPORT")
    print("=" * 70)
    print()
    print(report)
    print()
    print("=" * 70)
    print("END OF REPORT")
    print("=" * 70)

    logger.info("Research source verification completed successfully.")


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()