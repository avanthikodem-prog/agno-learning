import logging
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS

from agno.agent import Agent
from agno.models.ollama import Ollama


# ======================================================================
# LOGGING
# ======================================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_cross_source_fact_checking")


# ======================================================================
# CONFIGURATION
# ======================================================================

RESEARCH_QUESTION = (
    "How can AI-powered voice assistants help farmers in rural India?"
)

OLLAMA_MODEL = "llama3.2"

MAX_SEARCH_RESULTS_PER_QUERY = 5
MAX_UNIQUE_SOURCES = 15
MAX_VERIFIED_SOURCES = 10
MAX_CLAIMS = 6
MAX_SOURCES_PER_CLAIM = 3

MIN_CONTENT_LENGTH = 200
MAX_CONTENT_LENGTH = 8000


# ======================================================================
# AGNO AGENT
# ======================================================================

def create_agent():
    """Create the local Ollama-powered Agno agent."""

    logger.info("Creating Agno agent with Ollama model: %s", OLLAMA_MODEL)

    return Agent(
        model=Ollama(id=OLLAMA_MODEL),
        markdown=False,
    )


# ======================================================================
# STEP 1 — GENERATE SEARCH QUERIES
# ======================================================================

def generate_search_queries(agent, research_question):
    """Generate focused search queries for the research question."""

    logger.info("Generating research search queries...")

    prompt = f"""
You are a research planning assistant.

Research question:
{research_question}

Generate exactly 5 focused web search queries.

Requirements:
- Stay strictly on the research question.
- Focus on AI-powered voice assistants.
- Focus on farmers in rural India.
- Cover benefits, agricultural advisory, multilingual voice access,
  farmer decision-making, and real-world implementations.
- Do not change the research topic.
- Return only one query per line.
- Do not number the queries.
"""

    response = agent.run(prompt)

    text = response.content.strip()

    queries = []

    for line in text.splitlines():
        cleaned = re.sub(r"^\s*[-*•\d.)]+\s*", "", line).strip()

        if cleaned and len(cleaned) > 15:
            queries.append(cleaned)

    queries = queries[:5]

    logger.info("Generated %d search queries.", len(queries))

    for index, query in enumerate(queries, start=1):
        logger.info("Query %d: %s", index, query)

    return queries


# ======================================================================
# STEP 2 — WEB SEARCH
# ======================================================================

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
                    }
                )

        logger.info("Found %d results for query.", len(results))

    except Exception as exc:
        logger.warning("Search failed: %s", exc)

    return results


# ======================================================================
# STEP 3 — URL VALIDATION
# ======================================================================

def is_valid_url(url):
    """Check whether a URL is usable."""

    try:
        parsed = urlparse(url)

        return (
            parsed.scheme in {"http", "https"}
            and bool(parsed.netloc)
        )

    except Exception:
        return False


# ======================================================================
# STEP 4 — DEDUPLICATE SOURCES
# ======================================================================

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

        if len(unique) >= MAX_UNIQUE_SOURCES:
            break

    logger.info(
        "Unique sources after deduplication: %d",
        len(unique),
    )

    return unique


# ======================================================================
# STEP 5 — FETCH ACTUAL SOURCE CONTENT
# ======================================================================

def fetch_source_content(url):
    """Fetch readable text from a webpage."""

    logger.info("Fetching source content: %s", url)

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/140 Safari/537.36"
        )
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            timeout=10,
        )

        logger.info(
            "HTTP status: %s",
            response.status_code,
        )

        if response.status_code != 200:
            logger.warning(
                "Skipping source because HTTP status was %s.",
                response.status_code,
            )
            return None

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for element in soup(
            ["script", "style", "noscript", "header", "footer", "nav", "form"]
        ):
            element.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        ).strip()

        if len(text) < MIN_CONTENT_LENGTH:
            logger.warning(
                "Very little readable content found."
            )
            return None

        text = text[:MAX_CONTENT_LENGTH]

        logger.info(
            "Extracted %d characters.",
            len(text),
        )

        return text

    except Exception as exc:
        logger.warning(
            "Failed to fetch source: %s",
            exc,
        )
        return None


# ======================================================================
# STEP 6 — COLLECT READABLE SOURCES
# ======================================================================

def collect_sources(sources):
    """Fetch readable content from sources."""

    logger.info(
        "Starting source-content collection..."
    )

    verified_sources = []

    for index, source in enumerate(
        sources,
        start=1,
    ):
        logger.info(
            "Processing source %d/%d",
            index,
            len(sources),
        )

        content = fetch_source_content(
            source["url"]
        )

        if not content:
            continue

        verified_sources.append(
            {
                "title": source["title"],
                "url": source["url"],
                "snippet": source["snippet"],
                "content": content,
            }
        )

        if len(verified_sources) >= MAX_VERIFIED_SOURCES:
            logger.info(
                "Reached maximum verified source limit: %d",
                MAX_VERIFIED_SOURCES,
            )
            break

    logger.info(
        "Successfully collected readable content from %d sources.",
        len(verified_sources),
    )

    return verified_sources


# ======================================================================
# STEP 7 — PREPARE EVIDENCE
# ======================================================================

def prepare_evidence(sources):
    """Prepare readable evidence with source identifiers."""

    logger.info("Preparing source evidence...")

    evidence_parts = []

    for index, source in enumerate(
        sources,
        start=1,
    ):
        evidence_parts.append(
            f"""
SOURCE {index}
TITLE: {source["title"]}
URL: {source["url"]}

CONTENT:
{source["content"]}
"""
        )

    evidence = "\n".join(evidence_parts)

    logger.info(
        "Prepared evidence from %d sources.",
        len(sources),
    )

    logger.info(
        "Total evidence size: %d characters.",
        len(evidence),
    )

    return evidence


# ======================================================================
# STEP 8 — GENERATE FACTUAL CLAIMS
# ======================================================================

def generate_claims(agent, research_question, evidence):
    """Generate factual claims strictly from collected evidence."""

    logger.info("Generating factual research claims...")

    prompt = f"""
You are a careful fact-checking researcher.

Research question:
{research_question}

Below is source evidence collected from real webpages.

{evidence}

Generate exactly {MAX_CLAIMS} concise factual claims.

STRICT RULES:
- Use ONLY information explicitly present in the evidence.
- Do not use outside knowledge.
- Do not invent statistics.
- Do not create claims that are not directly supported by the evidence.
- Keep every claim short and specific.
- Each claim should be independently fact-checkable.
- Prefer claims that can be checked against multiple sources.
- Do not change the research question.

Return ONLY the claims.
One claim per line.
Do not number them.
"""

    response = agent.run(prompt)

    text = response.content.strip()

    claims = []

    for line in text.splitlines():
        cleaned = re.sub(
            r"^\s*[-*•\d.)]+\s*",
            "",
            line,
        ).strip()

        if not cleaned:
            continue

        if cleaned.lower().startswith(
            ("here are", "claims:", "factual claims:")
        ):
            continue

        claims.append(cleaned)

    claims = claims[:MAX_CLAIMS]

    logger.info(
        "Generated %d factual claims.",
        len(claims),
    )

    for index, claim in enumerate(
        claims,
        start=1,
    ):
        logger.info(
            "Claim %d: %s",
            index,
            claim,
        )

    return claims


# ======================================================================
# STEP 9 — FIND RELEVANT SOURCES FOR EACH CLAIM
# ======================================================================

def select_sources_for_claim(agent, claim, sources):
    """
    Ask the local model which sources are most relevant to a claim.

    Returns source numbers.
    """

    logger.info(
        "Selecting evidence sources for claim: %s",
        claim,
    )

    source_summary = []

    for index, source in enumerate(
        sources,
        start=1,
    ):
        source_summary.append(
            f"""
SOURCE {index}
TITLE: {source["title"]}
URL: {source["url"]}
SNIPPET: {source["snippet"]}
"""
        )

    available_sources = "\n".join(source_summary)

    prompt = f"""
You are selecting evidence for a fact-checking task.

CLAIM:
{claim}

AVAILABLE SOURCES:
{available_sources}

Select up to {MAX_SOURCES_PER_CLAIM} source numbers that are MOST relevant
to verifying this claim.

Rules:
- Select only sources that are directly relevant.
- Prefer independent sources.
- Do not select sources merely because their title contains similar words.
- Return ONLY source numbers separated by commas.
- Example: 1, 4, 7
"""

    try:
        response = agent.run(prompt)

        text = response.content.strip()

        numbers = re.findall(
            r"\b\d+\b",
            text,
        )

        selected = []

        for number in numbers:
            value = int(number)

            if (
                1 <= value <= len(sources)
                and value not in selected
            ):
                selected.append(value)

            if len(selected) >= MAX_SOURCES_PER_CLAIM:
                break

        logger.info(
            "Selected source numbers: %s",
            selected,
        )

        return selected

    except Exception as exc:
        logger.warning(
            "Could not select relevant sources: %s",
            exc,
        )

        return []


# ======================================================================
# STEP 10 — CROSS-SOURCE FACT CHECK
# ======================================================================

def cross_source_fact_check(
    agent,
    claim,
    selected_sources,
):
    """
    Compare multiple source contents and determine
    whether they agree or contradict each other.
    """

    logger.info(
        "Cross-checking claim against %d sources.",
        len(selected_sources),
    )

    evidence_parts = []

    for index, source in enumerate(
        selected_sources,
        start=1,
    ):
        evidence_parts.append(
            f"""
SOURCE {index}
TITLE: {source["title"]}
URL: {source["url"]}

CONTENT:
{source["content"]}
"""
        )

    evidence = "\n".join(evidence_parts)

    prompt = f"""
You are a strict cross-source fact checker.

CLAIM:
{claim}

SOURCE EVIDENCE:
{evidence}

Compare the sources carefully.

Determine:

1. VERDICT:
Choose exactly one:
SUPPORTED
PARTIALLY SUPPORTED
CONTRADICTED
UNSUPPORTED

2. AGREEMENT:
Do the sources agree with each other?

Choose:
HIGH
MEDIUM
LOW

3. CONFIDENCE:
Give a confidence score from 0 to 100.

4. REASON:
Explain briefly using ONLY the provided evidence.

Important:
- Do not use outside knowledge.
- Do not invent information.
- Do not treat a source merely mentioning a topic as proof of the claim.
- If sources directly agree, say so.
- If sources disagree, identify the contradiction.
- If only one source supports the claim, do not pretend there is multi-source agreement.

Return exactly this format:

VERDICT: ...
AGREEMENT: ...
CONFIDENCE: ...
REASON: ...
"""

    try:
        response = agent.run(prompt)

        text = response.content.strip()

        upper_text = text.upper()

        if "VERDICT: PARTIALLY SUPPORTED" in upper_text:
            verdict = "PARTIALLY SUPPORTED"
        elif "VERDICT: CONTRADICTED" in upper_text:
            verdict = "CONTRADICTED"
        elif "VERDICT: SUPPORTED" in upper_text:
            verdict = "SUPPORTED"
        else:
            verdict = "UNSUPPORTED"

        agreement_match = re.search(
            r"AGREEMENT:\s*(HIGH|MEDIUM|LOW)",
            upper_text,
        )

        agreement = (
            agreement_match.group(1)
            if agreement_match
            else "LOW"
        )

        confidence_match = re.search(
            r"CONFIDENCE:\s*(\d{1,3})",
            upper_text,
        )

        if confidence_match:
            confidence = int(
                confidence_match.group(1)
            )
            confidence = min(
                max(confidence, 0),
                100,
            )
        else:
            confidence = 0

        reason_match = re.search(
            r"REASON:\s*(.*)",
            text,
            re.IGNORECASE | re.DOTALL,
        )

        reason = (
            reason_match.group(1).strip()
            if reason_match
            else "No clear reason returned."
        )

        logger.info(
            "Verdict: %s | Agreement: %s | Confidence: %d%%",
            verdict,
            agreement,
            confidence,
        )

        return {
            "verdict": verdict,
            "agreement": agreement,
            "confidence": confidence,
            "reason": reason,
        }

    except Exception as exc:
        logger.warning(
            "Cross-source fact checking failed: %s",
            exc,
        )

        return {
            "verdict": "UNSUPPORTED",
            "agreement": "LOW",
            "confidence": 0,
            "reason": "Fact-checking failed.",
        }


# ======================================================================
# STEP 11 — VERIFY ALL CLAIMS
# ======================================================================

def verify_all_claims(
    agent,
    claims,
    sources,
):
    """Fact-check every claim using multiple sources."""

    logger.info(
        "Starting cross-source verification..."
    )

    results = []

    for index, claim in enumerate(
        claims,
        start=1,
    ):
        logger.info(
            "Fact-checking claim %d/%d",
            index,
            len(claims),
        )

        selected_numbers = select_sources_for_claim(
            agent,
            claim,
            sources,
        )

        selected_sources = [
            sources[number - 1]
            for number in selected_numbers
        ]

        if not selected_sources:
            logger.warning(
                "No relevant sources selected for claim %d.",
                index,
            )

            results.append(
                {
                    "claim": claim,
                    "sources": [],
                    "verdict": "UNSUPPORTED",
                    "agreement": "LOW",
                    "confidence": 0,
                    "reason": "No relevant sources were selected.",
                }
            )

            continue

        verification = cross_source_fact_check(
            agent,
            claim,
            selected_sources,
        )

        results.append(
            {
                "claim": claim,
                "sources": selected_sources,
                **verification,
            }
        )

    logger.info(
        "Completed verification of %d claims.",
        len(results),
    )

    return results


# ======================================================================
# STEP 12 — DISPLAY RESULTS
# ======================================================================

def display_results(results):
    """Display cross-source fact-check results."""

    print()
    print("=" * 70)
    print("CROSS-SOURCE FACT CHECKING RESULTS")
    print("=" * 70)

    for index, result in enumerate(
        results,
        start=1,
    ):
        print()
        print(f"CLAIM {index}")
        print("-" * 70)
        print(result["claim"])

        print()
        print(f"VERDICT: {result['verdict']}")
        print(f"AGREEMENT: {result['agreement']}")
        print(f"CONFIDENCE: {result['confidence']}%")

        print()
        print("SOURCES USED:")

        for source in result["sources"]:
            print(f"- {source['title']}")
            print(f"  {source['url']}")

        print()
        print("REASON:")
        print(result["reason"])


# ======================================================================
# STEP 13 — FINAL REPORT
# ======================================================================

def generate_final_report(
    agent,
    research_question,
    results,
):
    """Generate the final cross-source verified report."""

    logger.info(
        "Generating final cross-source research report..."
    )

    result_text = []

    for index, result in enumerate(
        results,
        start=1,
    ):
        source_names = ", ".join(
            source["title"]
            for source in result["sources"]
        )

        result_text.append(
            f"""
CLAIM {index}:
{result["claim"]}

VERDICT:
{result["verdict"]}

AGREEMENT:
{result["agreement"]}

CONFIDENCE:
{result["confidence"]}%

REASON:
{result["reason"]}

SOURCES:
{source_names}
"""
        )

    verification_data = "\n".join(
        result_text
    )

    prompt = f"""
You are a professional research-report writer.

Original research question:
{research_question}

Below are cross-source fact-checking results:

{verification_data}

Create a final evidence-based report.

IMPORTANT:
- Keep the original research question exactly unchanged.
- Do not introduce new facts.
- Do not invent statistics.
- Do not turn unsupported claims into findings.
- Clearly distinguish supported, partially supported,
  contradicted, and unsupported claims.
- Use confidence scores when discussing evidence strength.
- Mention when evidence comes from only one source.
- Do not claim that a source was verified beyond the information
  actually provided.

Use exactly these sections:

Research Question

Executive Summary

High-Confidence Findings

Medium-Confidence Findings

Contradicted or Partially Supported Findings

Unsupported Findings

Evidence Limitations

Conclusion

Sources

Keep the report concise but informative.
"""

    try:
        response = agent.run(prompt)

        report = response.content.strip()

        logger.info(
            "Final report generated: %d characters.",
            len(report),
        )

        return report

    except Exception as exc:
        logger.error(
            "Final report generation failed: %s",
            exc,
        )

        return "Final report generation failed."


# ======================================================================
# MAIN
# ======================================================================

def main():

    logger.info("=" * 70)
    logger.info(
        "Starting Cross-Source Fact Checking"
    )
    logger.info("=" * 70)

    logger.info(
        "Research question: %s",
        RESEARCH_QUESTION,
    )

    # --------------------------------------------------------------
    # Create agent
    # --------------------------------------------------------------

    agent = create_agent()

    # --------------------------------------------------------------
    # Generate search queries
    # --------------------------------------------------------------

    queries = generate_search_queries(
        agent,
        RESEARCH_QUESTION,
    )

    if not queries:
        logger.error(
            "No search queries were generated."
        )
        return

    # --------------------------------------------------------------
    # Search web
    # --------------------------------------------------------------

    all_sources = []

    for query in queries:
        results = search_web(query)
        all_sources.extend(results)

    logger.info(
        "Total raw sources collected: %d",
        len(all_sources),
    )

    if not all_sources:
        logger.error(
            "No web sources were collected."
        )
        return

    # --------------------------------------------------------------
    # Deduplicate
    # --------------------------------------------------------------

    unique_sources = deduplicate_sources(
        all_sources
    )

    if not unique_sources:
        logger.error(
            "No unique valid sources available."
        )
        return

    # --------------------------------------------------------------
    # Fetch actual content
    # --------------------------------------------------------------

    verified_sources = collect_sources(
        unique_sources
    )

    if not verified_sources:
        logger.error(
            "No readable sources were available."
        )
        return

    # --------------------------------------------------------------
    # Prepare evidence
    # --------------------------------------------------------------

    evidence = prepare_evidence(
        verified_sources
    )

    logger.info(
        "Evidence prepared successfully."
    )

    # --------------------------------------------------------------
    # Generate claims
    # --------------------------------------------------------------

    claims = generate_claims(
        agent,
        RESEARCH_QUESTION,
        evidence,
    )

    if not claims:
        logger.error(
            "No claims were generated."
        )
        return

    # --------------------------------------------------------------
    # Cross-source verification
    # --------------------------------------------------------------

    verification_results = verify_all_claims(
        agent,
        claims,
        verified_sources,
    )

    # --------------------------------------------------------------
    # Display results
    # --------------------------------------------------------------

    display_results(
        verification_results
    )

    # --------------------------------------------------------------
    # Generate final report
    # --------------------------------------------------------------

    final_report = generate_final_report(
        agent,
        RESEARCH_QUESTION,
        verification_results,
    )

    print()
    print("=" * 70)
    print("FINAL CROSS-SOURCE VERIFIED RESEARCH REPORT")
    print("=" * 70)
    print(final_report)
    print("=" * 70)
    print("END OF REPORT")
    print("=" * 70)

    logger.info(
        "Cross-source fact checking completed successfully."
    )


# ======================================================================
# PROGRAM ENTRY POINT
# ======================================================================

if __name__ == "__main__":
    main()