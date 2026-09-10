"""
Exercise 59 - Claim Verification & Hallucination Detection

Pipeline:
Research Question
        ↓
Generate Search Queries
        ↓
Web Search
        ↓
Deduplicate Sources
        ↓
Fetch Actual Source Content
        ↓
Generate Research Claims
        ↓
Verify Each Claim Against Evidence
        ↓
SUPPORTED / PARTIALLY SUPPORTED / UNSUPPORTED
        ↓
Final Verified Report
"""

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

logger = logging.getLogger("gram_swaram_claim_verification")


# ============================================================
# CONFIGURATION
# ============================================================

RESEARCH_QUESTION = (
    "How can AI-powered voice assistants help farmers in rural India?"
)

OLLAMA_MODEL = "llama3.2"

MAX_SEARCH_RESULTS_PER_QUERY = 5
MAX_UNIQUE_SOURCES = 15
MAX_VERIFIED_SOURCES = 8

MIN_CONTENT_LENGTH = 200
MAX_CONTENT_LENGTH = 10000


# ============================================================
# AGNO / OLLAMA
# ============================================================

def create_agent(instructions):
    """Create an Agno agent using local Ollama."""

    return Agent(
        model=Ollama(id=OLLAMA_MODEL),
        instructions=instructions,
        markdown=False,
    )


# ============================================================
# STEP 1 - GENERATE SEARCH QUERIES
# ============================================================

def generate_search_queries(question):
    """Generate focused research queries."""

    logger.info("Generating research search queries...")

    agent = create_agent(
        [
            "You are a research planning assistant.",
            "Generate exactly 5 focused web search queries.",
            "The queries must stay strictly focused on the original research question.",
            "Do not change the research topic.",
            "Do not introduce unrelated topics.",
            "Return one query per line.",
            "Do not number the queries.",
        ]
    )

    response = agent.run(
        f"""
Original research question:

{question}

Generate 5 focused search queries for researching this exact question.
"""
    )

    text = response.content if hasattr(response, "content") else str(response)

    queries = []

    for line in text.splitlines():
        line = line.strip()

        line = re.sub(r"^[\-\*\d\.\)\s]+", "", line)
        line = line.strip('"').strip("'").strip()

        if len(line) >= 20:
            queries.append(line)

    queries = queries[:5]

    logger.info("Generated %d search queries.", len(queries))

    for index, query in enumerate(queries, start=1):
        logger.info("Query %d: %s", index, query)

    return queries


# ============================================================
# STEP 2 - SEARCH WEB
# ============================================================

def search_web(query):
    """Search the web using DDGS."""

    logger.info("Searching: %s", query)

    results = []

    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(
                query,
                max_results=MAX_SEARCH_RESULTS_PER_QUERY,
            )

            for item in search_results:
                url = item.get("href") or item.get("url")

                if not url:
                    continue

                results.append(
                    {
                        "title": item.get("title", "Untitled"),
                        "url": url,
                        "snippet": item.get("body", ""),
                        "query": query,
                    }
                )

    except Exception as exc:
        logger.warning("Search failed: %s", exc)

    logger.info("Found %d results for query.", len(results))

    return results


# ============================================================
# STEP 3 - URL VALIDATION
# ============================================================

def is_valid_url(url):
    """Check whether a URL is usable."""

    try:
        parsed = urlparse(url)

        if parsed.scheme not in {"http", "https"}:
            return False

        if not parsed.netloc:
            return False

        return True

    except Exception:
        return False


# ============================================================
# STEP 4 - DEDUPLICATION
# ============================================================

def deduplicate_sources(sources):
    """Remove duplicate URLs."""

    logger.info("Deduplicating sources...")

    unique = []
    seen_urls = set()

    for source in sources:

        url = source["url"].strip()

        if not is_valid_url(url):
            continue

        normalized_url = url.rstrip("/").lower()

        if normalized_url in seen_urls:
            continue

        seen_urls.add(normalized_url)
        unique.append(source)

    unique = unique[:MAX_UNIQUE_SOURCES]

    logger.info(
        "Unique sources after deduplication: %d",
        len(unique),
    )

    return unique


# ============================================================
# STEP 5 - FETCH ACTUAL SOURCE CONTENT
# ============================================================

def fetch_source_content(url):
    """Fetch and extract readable webpage content."""

    logger.info("Fetching source content: %s", url)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/140.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10,
        )

        logger.info("HTTP status: %s", response.status_code)

        if response.status_code != 200:
            logger.warning(
                "Could not fetch source. Status: %s",
                response.status_code,
            )
            return None

        soup = BeautifulSoup(response.text, "html.parser")

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

        text = soup.get_text(separator=" ")

        text = re.sub(r"\s+", " ", text).strip()

        if len(text) < MIN_CONTENT_LENGTH:
            logger.warning("Very little readable content found.")
            return None

        text = text[:MAX_CONTENT_LENGTH]

        logger.info("Extracted %d characters.", len(text))

        return text

    except requests.RequestException as exc:
        logger.warning("Request failed: %s", exc)
        return None

    except Exception as exc:
        logger.warning("Content extraction failed: %s", exc)
        return None


# ============================================================
# STEP 6 - COLLECT VERIFIED SOURCES
# ============================================================

def collect_verified_sources(sources):
    """Fetch actual content from candidate sources."""

    logger.info("Starting source-content verification...")

    verified = []

    for index, source in enumerate(sources, start=1):

        logger.info(
            "Processing source %d/%d",
            index,
            len(sources),
        )

        content = fetch_source_content(source["url"])

        if not content:
            logger.warning(
                "Skipping source: %s",
                source["url"],
            )
            continue

        verified_source = {
            "title": source["title"],
            "url": source["url"],
            "snippet": source["snippet"],
            "query": source["query"],
            "content": content,
        }

        verified.append(verified_source)

        if len(verified) >= MAX_VERIFIED_SOURCES:
            logger.info(
                "Reached maximum verified source limit: %d",
                MAX_VERIFIED_SOURCES,
            )
            break

    logger.info(
        "Successfully verified readable content from %d sources.",
        len(verified),
    )

    return verified


# ============================================================
# STEP 7 - PREPARE EVIDENCE
# ============================================================

def prepare_evidence(sources):
    """Create evidence package."""

    logger.info("Preparing evidence...")

    evidence_parts = []

    for index, source in enumerate(sources, start=1):

        evidence_parts.append(
            f"""
SOURCE {index}
Title: {source['title']}
URL: {source['url']}

Content:
{source['content']}
"""
        )

    evidence = "\n".join(evidence_parts)

    logger.info(
        "Prepared evidence from %d sources.",
        len(sources),
    )

    logger.info(
        "Evidence size: %d characters.",
        len(evidence),
    )

    return evidence


# ============================================================
# STEP 8 - GENERATE CLAIMS
# ============================================================

def generate_claims(question, evidence):
    """Generate claims using only provided evidence."""

    logger.info("Generating evidence-based claims...")

    agent = create_agent(
        [
            "You are an evidence extraction assistant.",
            "Use ONLY the provided source evidence.",
            "Do not use outside knowledge.",
            "Do not invent statistics.",
            "Do not invent percentages.",
            "Do not change the research question.",
            "Every claim must be traceable to the provided sources.",
            "Generate exactly 8 concise claims.",
            "Return one claim per line.",
        ]
    )

    response = agent.run(
        f"""
Original research question:

{question}

SOURCE EVIDENCE:

{evidence}

Generate 8 factual research claims that are directly supported
or potentially testable using ONLY the source evidence above.

Do not introduce information that does not appear in the evidence.
"""
    )

    text = response.content if hasattr(response, "content") else str(response)

    claims = []

    for line in text.splitlines():

        line = line.strip()

        line = re.sub(r"^[\-\*\d\.\)\s]+", "", line)

        if len(line) >= 20:
            claims.append(line)

    claims = claims[:8]

    logger.info("Generated %d claims.", len(claims))

    for index, claim in enumerate(claims, start=1):
        logger.info("Claim %d: %s", index, claim)

    return claims


# ============================================================
# STEP 9 - VERIFY ONE CLAIM
# ============================================================

def verify_claim(claim, evidence):
    """Verify one claim against the evidence."""

    logger.info("Verifying claim...")

    agent = create_agent(
        [
            "You are a strict fact-checking assistant.",
            "Use ONLY the provided evidence.",
            "Do not use outside knowledge.",
            "Do not assume that a source supports a claim.",
            "A claim is SUPPORTED only when evidence clearly supports it.",
            "A claim is PARTIALLY SUPPORTED when evidence supports only part of it.",
            "A claim is UNSUPPORTED when evidence does not establish it.",
            "Never invent evidence.",
            "Never invent statistics.",
            "Return exactly:",
            "VERDICT: SUPPORTED or PARTIALLY SUPPORTED or UNSUPPORTED",
            "EVIDENCE: short explanation",
        ]
    )

    response = agent.run(
        f"""
CLAIM:

{claim}

SOURCE EVIDENCE:

{evidence}

Fact-check the claim strictly against the evidence.
"""
    )

    text = response.content if hasattr(response, "content") else str(response)

    upper_text = text.upper()

    if "VERDICT: PARTIALLY SUPPORTED" in upper_text:
        verdict = "PARTIALLY SUPPORTED"

    elif "VERDICT: UNSUPPORTED" in upper_text:
        verdict = "UNSUPPORTED"

    elif "VERDICT: SUPPORTED" in upper_text:
        verdict = "SUPPORTED"

    else:
        verdict = "UNSUPPORTED"

    evidence_match = re.search(
        r"EVIDENCE:\s*(.*)",
        text,
        re.IGNORECASE | re.DOTALL,
    )

    explanation = (
        evidence_match.group(1).strip()
        if evidence_match
        else "No clear evidence explanation returned."
    )

    return {
        "claim": claim,
        "verdict": verdict,
        "explanation": explanation,
    }


# ============================================================
# STEP 10 - VERIFY ALL CLAIMS
# ============================================================

def verify_all_claims(claims, evidence):
    """Fact-check every generated claim."""

    logger.info("Starting claim verification...")

    verified_claims = []

    for index, claim in enumerate(claims, start=1):

        logger.info(
            "Fact-checking claim %d/%d",
            index,
            len(claims),
        )

        result = verify_claim(
            claim,
            evidence,
        )

        verified_claims.append(result)

        logger.info(
            "Claim %d verdict: %s",
            index,
            result["verdict"],
        )

    return verified_claims


# ============================================================
# STEP 11 - DISPLAY RESULTS
# ============================================================

def display_claim_results(results):
    """Display claim verification results."""

    print()
    print("=" * 70)
    print("CLAIM VERIFICATION RESULTS")
    print("=" * 70)

    for index, result in enumerate(results, start=1):

        print()
        print(f"CLAIM {index}")
        print("-" * 70)

        print(result["claim"])

        print()
        print(f"VERDICT: {result['verdict']}")

        print(f"EVIDENCE: {result['explanation']}")

    print()
    print("=" * 70)


# ============================================================
# STEP 12 - FINAL VERIFIED REPORT
# ============================================================

def generate_final_report(
    question,
    sources,
    verified_claims,
):
    """Generate final report using verified claims only."""

    logger.info("Generating final verified research report...")

    claim_text = []

    for index, result in enumerate(
        verified_claims,
        start=1,
    ):
        claim_text.append(
            f"""
CLAIM {index}
Claim: {result['claim']}
Verdict: {result['verdict']}
Explanation: {result['explanation']}
"""
        )

    claims = "\n".join(claim_text)

    source_text = []

    for index, source in enumerate(
        sources,
        start=1,
    ):
        source_text.append(
            f"{index}. {source['title']} — {source['url']}"
        )

    sources_formatted = "\n".join(source_text)

    agent = create_agent(
        [
            "You are a strict research report writer.",
            "The original research question MUST remain unchanged.",
            "Use ONLY the verified claims provided.",
            "Do not invent facts.",
            "Do not invent statistics.",
            "Do not add companies or sources that were not provided.",
            "Clearly identify unsupported claims.",
            "Do not convert unsupported claims into facts.",
            "Keep the report evidence-based.",
            "Use exactly these sections:",
            "Research Question",
            "Executive Summary",
            "Supported Findings",
            "Partially Supported Findings",
            "Unsupported Claims",
            "Evidence Limitations",
            "Conclusion",
            "Sources",
        ]
    )

    response = agent.run(
        f"""
ORIGINAL RESEARCH QUESTION:

{question}

VERIFIED CLAIMS:

{claims}

SOURCES USED:

{sources_formatted}

Generate the final research report.

IMPORTANT:
1. Keep the original research question exactly as provided.
2. Use only the verified claims.
3. Clearly separate supported, partially supported, and unsupported claims.
4. Do not invent percentages or statistics.
5. Do not introduce unrelated topics.
"""
    )

    report = response.content if hasattr(response, "content") else str(response)

    logger.info(
        "Final verified report generated: %d characters.",
        len(report),
    )

    return report


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info("=" * 70)
    logger.info("Starting Claim Verification & Hallucination Detection")
    logger.info("=" * 70)

    logger.info(
        "Research question: %s",
        RESEARCH_QUESTION,
    )

    # STEP 1
    queries = generate_search_queries(
        RESEARCH_QUESTION
    )

    if not queries:
        logger.error("No search queries generated.")
        return

    # STEP 2
    all_sources = []

    for query in queries:
        results = search_web(query)
        all_sources.extend(results)

    logger.info(
        "Total raw sources collected: %d",
        len(all_sources),
    )

    if not all_sources:
        logger.error("No sources found.")
        return

    # STEP 3
    unique_sources = deduplicate_sources(
        all_sources
    )

    if not unique_sources:
        logger.error("No valid unique sources found.")
        return

    # STEP 4
    verified_sources = collect_verified_sources(
        unique_sources
    )

    if not verified_sources:
        logger.error(
            "No readable source content was available."
        )
        return

    # STEP 5
    evidence = prepare_evidence(
        verified_sources
    )

    # STEP 6
    claims = generate_claims(
        RESEARCH_QUESTION,
        evidence,
    )

    if not claims:
        logger.error("No research claims generated.")
        return

    # STEP 7
    verified_claims = verify_all_claims(
        claims,
        evidence,
    )

    # STEP 8
    display_claim_results(
        verified_claims
    )

    # STEP 9
    final_report = generate_final_report(
        RESEARCH_QUESTION,
        verified_sources,
        verified_claims,
    )

    # STEP 10
    print()
    print("=" * 70)
    print("FINAL CLAIM-VERIFIED RESEARCH REPORT")
    print("=" * 70)

    print(final_report)

    print("=" * 70)
    print("END OF REPORT")
    print("=" * 70)

    logger.info(
        "Claim verification completed successfully."
    )


if __name__ == "__main__":
    main()