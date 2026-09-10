import logging
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
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

logger = logging.getLogger("gram_swaram_content_verification")


# ============================================================
# CONFIGURATION
# ============================================================

RESEARCH_QUESTION = (
    "How can AI-powered voice assistants help farmers in rural India?"
)

MAX_RESULTS_PER_QUERY = 5
MAX_SOURCE_CONTENT = 8
MINIMUM_SOURCES = 5

REQUEST_TIMEOUT = 10

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 Chrome/120 Safari/537.36"
)


# ============================================================
# STEP 1 — GENERATE SEARCH QUERIES
# ============================================================

def generate_search_queries(question: str) -> list[str]:
    """
    Generate multiple research queries using Agno + Ollama.
    """

    logger.info("Generating research search queries...")

    planner = Agent(
        model=Ollama(id="llama3.2"),
        instructions=[
            "You are a research planning assistant.",
            "Generate exactly 6 useful web search queries.",
            "Focus on AI-powered voice assistants and agriculture in India.",
            "Cover government initiatives, academic research, farmer adoption,",
            "benefits, limitations, and real-world implementations.",
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

Generate six research queries.
"""
    )

    text = response.content.strip()

    queries = []

    for line in text.splitlines():

        cleaned = re.sub(
            r"^\s*[-*•\d.)]+\s*",
            "",
            line,
        ).strip()

        if cleaned and len(cleaned) > 10:
            queries.append(cleaned)

    queries = list(dict.fromkeys(queries))

    logger.info(
        "Generated %d search queries.",
        len(queries),
    )

    for index, query in enumerate(queries[:6], start=1):
        logger.info(
            "Query %d: %s",
            index,
            query,
        )

    return queries[:6]


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

                    title = result.get(
                        "title",
                        "",
                    ).strip()

                    url = result.get(
                        "href",
                        "",
                    ).strip()

                    snippet = result.get(
                        "body",
                        "",
                    ).strip()

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
                    "Search failed for '%s': %s",
                    query,
                    exc,
                )

    logger.info(
        "Total raw sources collected: %d",
        len(all_sources),
    )

    return all_sources


# ============================================================
# STEP 3 — DEDUPLICATE SOURCES
# ============================================================

def deduplicate_sources(
    sources: list[dict],
) -> list[dict]:
    """
    Remove duplicate URLs.
    """

    logger.info("Deduplicating sources...")

    unique_sources = []
    seen_urls = set()

    for source in sources:

        url = source["url"].rstrip("/").lower()

        if url in seen_urls:
            continue

        seen_urls.add(url)

        unique_sources.append(source)

    logger.info(
        "Unique sources after deduplication: %d",
        len(unique_sources),
    )

    return unique_sources


# ============================================================
# STEP 4 — DOMAIN CLASSIFICATION
# ============================================================

def extract_domain(url: str) -> str:
    """
    Extract domain from URL.
    """

    try:

        domain = urlparse(url).netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    except Exception:

        return ""


def classify_source_type(domain: str) -> str:
    """
    Classify source using deterministic rules.
    """

    domain = domain.lower()

    # Government
    if (
        domain.endswith(".gov.in")
        or domain.endswith(".gov")
        or ".gov.in" in domain
    ):
        return "Government / Official"

    # Academic / Research
    academic_domains = [
        "springer.com",
        "link.springer.com",
        "nature.com",
        "sciencedirect.com",
        "ieee.org",
        "arxiv.org",
        "pubmed.ncbi.nlm.nih.gov",
        "ncbi.nlm.nih.gov",
        "researchgate.net",
        ".edu",
        ".ac.in",
    ]

    if any(
        item in domain
        for item in academic_domains
    ):
        return "Academic / Research"

    # International institutions
    institutional_domains = [
        "worldbank.org",
        "oecd.org",
        "ifpri.org",
        "fao.org",
        "un.org",
    ]

    if any(
        item in domain
        for item in institutional_domains
    ):
        return "Institutional / International"

    # News
    news_domains = [
        "reuters.com",
        "bbc.com",
        "bbc.co.uk",
        "thehindu.com",
        "indianexpress.com",
        "hindustantimes.com",
        "financialexpress.com",
        "economictimes.indiatimes.com",
        "techcrunch.com",
        "thebetterindia.com",
    ]

    if any(
        item in domain
        for item in news_domains
    ):
        return "News / Industry"

    # Commercial
    commercial_domains = [
        "bing.com",
        "facebook.com",
    ]

    if any(
        item in domain
        for item in commercial_domains
    ):
        return "Platform / Commercial"

    if (
        domain.endswith(".com")
        or domain.endswith(".ai")
        or domain.endswith(".io")
        or domain.endswith(".co")
    ):
        return "Company / Commercial"

    return "Other"


# ============================================================
# STEP 5 — PRELIMINARY SOURCE SCORE
# ============================================================

def calculate_source_score(
    source_type: str,
) -> int:
    """
    Calculate a preliminary score.

    This is NOT proof that the content is factually correct.
    """

    scores = {
        "Government / Official": 10,
        "Academic / Research": 9,
        "Institutional / International": 9,
        "News / Industry": 7,
        "Platform / Commercial": 4,
        "Company / Commercial": 5,
        "Other": 3,
    }

    return scores.get(
        source_type,
        3,
    )


# ============================================================
# STEP 6 — FETCH ACTUAL SOURCE CONTENT
# ============================================================

def fetch_source_content(
    url: str,
) -> str | None:
    """
    Fetch the actual webpage and extract visible text.

    Search snippets are not enough for strong evidence.
    """

    logger.info(
        "Fetching source content: %s",
        url,
    )

    try:

        response = requests.get(
            url,
            headers={
                "User-Agent": USER_AGENT,
            },
            timeout=REQUEST_TIMEOUT,
        )

        logger.info(
            "HTTP status: %s",
            response.status_code,
        )

        if response.status_code != 200:

            logger.warning(
                "Could not fetch source. Status: %s",
                response.status_code,
            )

            return None

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        # Remove unnecessary HTML elements
        for element in soup(
            [
                "script",
                "style",
                "noscript",
                "header",
                "footer",
                "nav",
                "form",
            ]
        ):
            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True,
        )

        # Normalize whitespace
        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        if len(text) < 200:

            logger.warning(
                "Very little readable content found."
            )

            return None

        # Prevent extremely large pages
        text = text[:12000]

        logger.info(
            "Extracted %d characters.",
            len(text),
        )

        return text

    except requests.RequestException as exc:

        logger.warning(
            "Request failed: %s",
            exc,
        )

        return None

    except Exception as exc:

        logger.warning(
            "Content extraction failed: %s",
            exc,
        )

        return None


# ============================================================
# STEP 7 — VERIFY RELEVANCE WITH AGNO + OLLAMA
# ============================================================

def evaluate_source_with_ai(
    question: str,
    source: dict,
) -> dict:
    """
    Ask Ollama to evaluate the actual source content.

    This is AI-assisted evaluation, not absolute verification.
    """

    logger.info(
        "AI-evaluating source: %s",
        source["domain"],
    )

    evaluator = Agent(
        model=Ollama(id="llama3.2"),
        instructions=[
            "You are a careful research source evaluator.",
            "Evaluate only the supplied source content.",
            "Do not invent information.",
            "Do not assume a claim is true simply because it appears on the page.",
            "Return exactly these four lines:",
            "RELEVANCE: 0-10",
            "EVIDENCE: 0-10",
            "PROMOTIONAL_RISK: 0-10",
            "REASON: short explanation",
        ],
        markdown=False,
    )

    content = source["content"][:8000]

    prompt = f"""
Research question:
{question}

Source title:
{source["title"]}

Source URL:
{source["url"]}

Source type:
{source["source_type"]}

Actual source content:
{content}

Evaluate this source.
"""

    try:

        response = evaluator.run(prompt)

        result_text = response.content.strip()

        relevance = extract_score(
            result_text,
            "RELEVANCE",
        )

        evidence = extract_score(
            result_text,
            "EVIDENCE",
        )

        promotional_risk = extract_score(
            result_text,
            "PROMOTIONAL_RISK",
        )

        reason_match = re.search(
            r"REASON:\s*(.*)",
            result_text,
            re.IGNORECASE,
        )

        reason = (
            reason_match.group(1).strip()
            if reason_match
            else "No reason provided."
        )

        return {
            "ai_relevance": relevance,
            "ai_evidence": evidence,
            "ai_promotional_risk": promotional_risk,
            "ai_reason": reason,
        }

    except Exception as exc:

        logger.warning(
            "AI evaluation failed: %s",
            exc,
        )

        return {
            "ai_relevance": 0,
            "ai_evidence": 0,
            "ai_promotional_risk": 10,
            "ai_reason": "AI evaluation failed.",
        }


# ============================================================
# STEP 8 — EXTRACT AI SCORE
# ============================================================

def extract_score(
    text: str,
    field: str,
) -> int:
    """
    Extract a 0-10 score from AI output.
    """

    pattern = rf"{field}\s*:\s*(\d+)"

    match = re.search(
        pattern,
        text,
        re.IGNORECASE,
    )

    if not match:
        return 0

    score = int(match.group(1))

    return max(
        0,
        min(score, 10),
    )


# ============================================================
# STEP 9 — CALCULATE FINAL QUALITY SCORE
# ============================================================

def calculate_final_quality_score(
    source: dict,
) -> float:
    """
    Combine deterministic source score with AI-assisted scores.

    Formula:
    30% source type
    30% relevance
    30% evidence
    10% promotional-risk adjustment
    """

    rule_score = source["rule_score"]

    relevance = source["ai_relevance"]

    evidence = source["ai_evidence"]

    promotional_risk = source[
        "ai_promotional_risk"
    ]

    promotional_safety = 10 - promotional_risk

    final_score = (
        rule_score * 0.30
        + relevance * 0.30
        + evidence * 0.30
        + promotional_safety * 0.10
    )

    return round(
        final_score,
        2,
    )


# ============================================================
# STEP 10 — PROCESS SOURCE
# ============================================================

def process_source(
    question: str,
    source: dict,
) -> dict | None:
    """
    Fetch and evaluate one source.
    """

    domain = extract_domain(
        source["url"]
    )

    if not domain:

        logger.warning(
            "Invalid domain: %s",
            source["url"],
        )

        return None

    source_type = classify_source_type(
        domain
    )

    rule_score = calculate_source_score(
        source_type
    )

    content = fetch_source_content(
        source["url"]
    )

    if not content:

        logger.warning(
            "Skipping source because content could not be extracted: %s",
            domain,
        )

        return None

    processed_source = {
        **source,
        "domain": domain,
        "source_type": source_type,
        "rule_score": rule_score,
        "content": content,
    }

    ai_evaluation = evaluate_source_with_ai(
        question,
        processed_source,
    )

    processed_source.update(
        ai_evaluation
    )

    processed_source[
        "final_quality_score"
    ] = calculate_final_quality_score(
        processed_source
    )

    return processed_source


# ============================================================
# STEP 11 — PREPARE VERIFIED EVIDENCE
# ============================================================

def prepare_verified_evidence(
    sources: list[dict],
) -> str:
    """
    Prepare actual webpage content from the highest-quality sources.
    """

    selected_sources = sources[
        :MAX_SOURCE_CONTENT
    ]

    evidence_parts = []

    for index, source in enumerate(
        selected_sources,
        start=1,
    ):

        evidence_parts.append(
            f"""
==================================================
SOURCE {index}
==================================================

Title:
{source["title"]}

URL:
{source["url"]}

Domain:
{source["domain"]}

Source Type:
{source["source_type"]}

Rule Score:
{source["rule_score"]}/10

AI Relevance:
{source["ai_relevance"]}/10

AI Evidence Strength:
{source["ai_evidence"]}/10

AI Promotional Risk:
{source["ai_promotional_risk"]}/10

Final Quality Score:
{source["final_quality_score"]}/10

AI Evaluation Reason:
{source["ai_reason"]}

ACTUAL SOURCE CONTENT:
{source["content"][:7000]}
"""
        )

    evidence = "\n".join(
        evidence_parts
    )

    logger.info(
        "Prepared verified evidence from %d sources.",
        len(selected_sources),
    )

    logger.info(
        "Final evidence size: %d characters.",
        len(evidence),
    )

    return evidence


# ============================================================
# STEP 12 — FINAL RESEARCH REPORT
# ============================================================

def generate_final_report(
    question: str,
    evidence: str,
) -> str:
    """
    Generate final evidence-based research report.
    """

    logger.info(
        "Generating final research report..."
    )

    researcher = Agent(
        model=Ollama(id="llama3.2"),
        instructions=[
            "You are an evidence-based research analyst.",
            "Use only the supplied source content.",
            "Do not invent facts or statistics.",
            "Do not invent URLs.",
            "Clearly distinguish source claims from your interpretation.",
            "If sources disagree, explain the disagreement.",
            "Do not claim independent verification.",
            "Mention evidence limitations when appropriate.",
        ],
        markdown=False,
    )

    prompt = f"""
Research question:

{question}

Verified source content:

{evidence}

Create a structured research report with:

1. Research Question
2. Executive Summary
3. Search Strategy
4. Source Verification Method
5. Key Findings
6. Evidence Analysis
7. Opportunities
8. Challenges and Risks
9. Evidence Gaps
10. Source Quality Assessment
11. Conclusion
12. Sources

Important:

- Base findings on the actual source content supplied.
- Do not rely only on search snippets.
- Do not treat quality scores as proof of truth.
- Mention promotional risk where appropriate.
- Do not invent adoption statistics.
- If there is insufficient evidence for a claim, say so.
"""

    response = researcher.run(
        prompt
    )

    report = response.content.strip()

    logger.info(
        "Final report generated: %d characters.",
        len(report),
    )

    return report


# ============================================================
# STEP 13 — MAIN PIPELINE
# ============================================================

def main() -> None:

    logger.info(
        "=========================================="
    )

    logger.info(
        "Starting Source Content Verification"
    )

    logger.info(
        "=========================================="
    )

    logger.info(
        "Research question: %s",
        RESEARCH_QUESTION,
    )

    # --------------------------------------------------------
    # 1. Generate queries
    # --------------------------------------------------------

    queries = generate_search_queries(
        RESEARCH_QUESTION
    )

    if not queries:

        logger.error(
            "No search queries generated."
        )

        return

    # --------------------------------------------------------
    # 2. Search
    # --------------------------------------------------------

    raw_sources = search_web(
        queries
    )

    if not raw_sources:

        logger.error(
            "No search results found."
        )

        return

    # --------------------------------------------------------
    # 3. Deduplicate
    # --------------------------------------------------------

    unique_sources = deduplicate_sources(
        raw_sources
    )

    # --------------------------------------------------------
    # 4. Process actual source content
    # --------------------------------------------------------

    logger.info(
        "Starting actual webpage content verification..."
    )

    processed_sources = []

    for index, source in enumerate(
        unique_sources,
        start=1,
    ):

        logger.info(
            "Processing source %d/%d",
            index,
            len(unique_sources),
        )

        processed = process_source(
            RESEARCH_QUESTION,
            source,
        )

        if processed:

            processed_sources.append(
                processed
            )

    logger.info(
        "Successfully processed %d sources.",
        len(processed_sources),
    )

    # --------------------------------------------------------
    # 5. Check minimum sources
    # --------------------------------------------------------

    if len(processed_sources) < MINIMUM_SOURCES:

        logger.warning(
            "Only %d sources had readable content. Recommended minimum: %d",
            len(processed_sources),
            MINIMUM_SOURCES,
        )

    else:

        logger.info(
            "Content verification source check passed."
        )

    if not processed_sources:

        logger.error(
            "No sources with readable content were available."
        )

        return

    # --------------------------------------------------------
    # 6. Sort by final quality score
    # --------------------------------------------------------

    processed_sources.sort(
        key=lambda source: source[
            "final_quality_score"
        ],
        reverse=True,
    )

    # --------------------------------------------------------
    # 7. Display quality ranking
    # --------------------------------------------------------

    logger.info(
        "========== VERIFIED SOURCE RANKING =========="
    )

    for index, source in enumerate(
        processed_sources,
        start=1,
    ):

        logger.info(
            "%d. %s | %s | Final Score: %.2f/10",
            index,
            source["domain"],
            source["source_type"],
            source["final_quality_score"],
        )

    # --------------------------------------------------------
    # 8. Prepare evidence
    # --------------------------------------------------------

    evidence = prepare_verified_evidence(
        processed_sources
    )

    # --------------------------------------------------------
    # 9. Generate final report
    # --------------------------------------------------------

    report = generate_final_report(
        RESEARCH_QUESTION,
        evidence,
    )

    # --------------------------------------------------------
    # 10. Display final report
    # --------------------------------------------------------

    print()
    print("=" * 70)
    print("FINAL SOURCE-CONTENT VERIFIED RESEARCH REPORT")
    print("=" * 70)
    print()
    print(report)
    print()
    print("=" * 70)
    print("END OF REPORT")
    print("=" * 70)

    logger.info(
        "Source content verification completed successfully."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()