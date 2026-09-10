"""
Exercise 61.4.1
Final Research Confidence System - Robust Claim Generation

Pipeline:
Research Question
    ↓
AI-generated search queries
    ↓
Clean queries
    ↓
Web search
    ↓
Source filtering
    ↓
Source ranking
    ↓
Fetch source content
    ↓
Evidence extraction
    ↓
Evidence cards
    ↓
LLM claim generation
    ↓
Robust claim parsing
    ↓
Deterministic fallback claim generation
    ↓
Claim-to-source mapping
    ↓
LLM verification
    ↓
Evidence overlap check
    ↓
Strict Python verdict
    ↓
Confidence scoring
    ↓
Deterministic final report
"""

import logging
import re
from collections import Counter
from typing import Dict, List, Set

import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from ollama import chat


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("final_research_confidence_system")


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "llama3.2"
OLLAMA_HOST = "http://127.0.0.1:11434"

MAX_QUERIES = 5
RESULTS_PER_QUERY = 5
MAX_CANDIDATE_SOURCES = 10
MAX_READABLE_SOURCES = 8
MAX_CLAIMS = 6

REQUEST_TIMEOUT = 15

RESEARCH_QUESTION = (
    "How can AI-powered voice assistants help farmers in rural India?"
)


# ============================================================
# SOURCE QUALITY
# ============================================================

def classify_source(url: str) -> str:
    """Classify source based on domain."""

    url_lower = url.lower()

    government_domains = [
        ".gov.in",
        "pib.gov.in",
        "icar.gov.in",
        "agricoop.gov.in",
        "meity.gov.in",
    ]

    academic_domains = [
        ".edu",
        ".ac.in",
        "iisc.ac.in",
        "iit.ac.in",
        "ieeexplore.ieee.org",
        "sciencedirect.com",
        "springer.com",
        "nature.com",
        "arxiv.org",
    ]

    institutional_domains = [
        "cgiar.org",
        "ifpri.org",
        "fao.org",
        "worldbank.org",
        "un.org",
        "undp.org",
    ]

    news_domains = [
        "reuters.com",
        "bbc.com",
        "thehindu.com",
        "indianexpress.com",
        "timesofindia.indiatimes.com",
    ]

    company_domains = [
        "microsoft.com",
        "google.com",
        "ibm.com",
        "nvidia.com",
        "amazon.com",
    ]

    platform_domains = [
        "medium.com",
        "linkedin.com",
        "scribd.com",
        "youtube.com",
    ]

    if any(domain in url_lower for domain in government_domains):
        return "Government"

    if any(domain in url_lower for domain in academic_domains):
        return "Academic/Research"

    if any(domain in url_lower for domain in institutional_domains):
        return "Institutional/International"

    if any(domain in url_lower for domain in news_domains):
        return "News/Industry"

    if any(domain in url_lower for domain in company_domains):
        return "Company"

    if any(domain in url_lower for domain in platform_domains):
        return "Platform/Commercial"

    return "Other"


QUALITY_SCORES = {
    "Government": 10,
    "Academic/Research": 9,
    "Institutional/International": 9,
    "News/Industry": 7,
    "Company": 5,
    "Platform/Commercial": 4,
    "Other": 3,
}


# ============================================================
# RELEVANCE
# ============================================================

RELEVANT_TERMS = {
    "ai": 2,
    "artificial intelligence": 3,
    "voice": 3,
    "voice assistant": 4,
    "voice technology": 4,
    "farmer": 3,
    "farmers": 3,
    "agriculture": 4,
    "agricultural": 4,
    "rural": 3,
    "india": 3,
    "indian": 3,
    "crop": 2,
    "advisory": 3,
    "language": 2,
    "local language": 4,
    "multilingual": 4,
}


def relevance_score(title: str, snippet: str, url: str) -> int:
    """Calculate simple deterministic relevance score."""

    text = f"{title} {snippet} {url}".lower()

    score = 0

    for term, points in RELEVANT_TERMS.items():
        if term in text:
            score += points

    return score


def is_irrelevant(title: str, snippet: str) -> bool:
    """Remove clearly unrelated search results."""

    text = f"{title} {snippet}".lower()

    irrelevant_patterns = [
        "job vacancy",
        "job openings",
        "recruitment",
        "salary",
        "course",
        "training institute",
        "stock price",
        "real estate",
        "hotel booking",
        "movie",
        "lyrics",
    ]

    return any(pattern in text for pattern in irrelevant_patterns)


# ============================================================
# QUERY GENERATION
# ============================================================

def generate_search_queries(question: str) -> List[str]:
    """Ask the local LLM to generate research queries."""

    prompt = f"""
You are a research planning assistant.

Research question:
{question}

Generate exactly 5 different web search queries.

The queries should focus on:
- AI voice assistants
- farmers
- rural India
- agriculture
- local languages
- practical applications
- real-world evidence

Return ONLY one query per line.

Do not number them.
Do not add explanations.
"""

    try:
        response = chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": 0,
            },
        )

        content = response["message"]["content"]

        queries = []

        for line in content.splitlines():
            cleaned = re.sub(r"^\s*[\d\-\*\.\)]+\s*", "", line).strip()

            if len(cleaned) >= 20:
                queries.append(cleaned)

        queries = queries[:MAX_QUERIES]

        if queries:
            logger.info(
                "Generated %d clean search queries.",
                len(queries),
            )

            for index, query in enumerate(queries, start=1):
                logger.info(
                    "Query %d: %s",
                    index,
                    query,
                )

            return queries

    except Exception as exc:
        logger.warning(
            "LLM query generation failed: %s",
            exc,
        )

    fallback_queries = [
        "AI voice assistants for agricultural advisory services rural Indian farmers local languages",
        "benefits of AI powered voice assistants for farmers in rural India",
        "AI voice assistants crop management decision making farmers India",
        "voice AI accessibility agricultural advisory rural India",
        "real world AI voice assistant applications Indian farmers agriculture",
    ]

    logger.warning(
        "Using deterministic fallback search queries."
    )

    return fallback_queries


# ============================================================
# WEB SEARCH
# ============================================================

def search_web(query: str) -> List[Dict]:
    """Search the web using DDGS."""

    results = []

    try:
        with DDGS() as ddgs:
            search_results = ddgs.text(
                query,
                max_results=RESULTS_PER_QUERY,
            )

            for item in search_results:
                title = item.get("title", "").strip()
                url = item.get("href", "").strip()
                snippet = item.get("body", "").strip()

                if not title or not url:
                    continue

                results.append(
                    {
                        "title": title,
                        "url": url,
                        "snippet": snippet,
                    }
                )

    except Exception as exc:
        logger.warning(
            "Search failed for query '%s': %s",
            query,
            exc,
        )

    return results


# ============================================================
# URL NORMALIZATION
# ============================================================

def normalize_url(url: str) -> str:
    """Normalize URLs for deduplication."""

    url = url.strip()

    url = re.sub(r"[?#].*$", "", url)

    if url.endswith("/"):
        url = url[:-1]

    return url.lower()


def deduplicate_sources(results: List[Dict]) -> List[Dict]:
    """Remove duplicate URLs."""

    seen: Set[str] = set()
    unique = []

    for item in results:
        normalized = normalize_url(item["url"])

        if normalized in seen:
            continue

        seen.add(normalized)

        item["normalized_url"] = normalized

        unique.append(item)

    return unique


# ============================================================
# SOURCE RANKING
# ============================================================

def rank_sources(sources: List[Dict]) -> List[Dict]:
    """Rank sources using quality and relevance."""

    for source in sources:
        source["quality_category"] = classify_source(
            source["url"]
        )

        source["quality_score"] = QUALITY_SCORES[
            source["quality_category"]
        ]

        source["relevance_score"] = relevance_score(
            source["title"],
            source["snippet"],
            source["url"],
        )

    filtered = []

    for source in sources:
        if is_irrelevant(
            source["title"],
            source["snippet"],
        ):
            continue

        if source["relevance_score"] < 3:
            continue

        filtered.append(source)

    filtered.sort(
        key=lambda item: (
            item["quality_score"],
            item["relevance_score"],
        ),
        reverse=True,
    )

    return filtered


# ============================================================
# FETCH SOURCE
# ============================================================

def fetch_source_content(url: str) -> str:
    """Fetch readable webpage text."""

    try:
        response = requests.get(
            url,
            timeout=REQUEST_TIMEOUT,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 "
                    "(Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 "
                    "(KHTML, like Gecko) "
                    "Chrome/131.0 Safari/537.36"
                )
            },
        )

        if response.status_code != 200:
            return ""

        soup = BeautifulSoup(
            response.text,
            "html.parser",
        )

        for element in soup(
            [
                "script",
                "style",
                "nav",
                "footer",
                "header",
                "aside",
                "noscript",
            ]
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

        if len(text) < 300:
            return ""

        return text[:12000]

    except Exception:
        return ""


# ============================================================
# EVIDENCE EXTRACTION
# ============================================================

def extract_evidence_sentences(
    text: str,
    question: str,
    max_sentences: int = 8,
) -> List[str]:
    """Extract useful sentences deterministically."""

    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    keywords = [
        "ai",
        "artificial intelligence",
        "voice",
        "farmer",
        "farmers",
        "agriculture",
        "agricultural",
        "rural",
        "india",
        "indian",
        "crop",
        "advisory",
        "language",
        "local language",
        "multilingual",
    ]

    scored = []

    for sentence in sentences:
        sentence = sentence.strip()

        if len(sentence) < 60:
            continue

        lower = sentence.lower()

        score = 0

        for keyword in keywords:
            if keyword in lower:
                score += 1

        if score >= 2:
            scored.append(
                (
                    score,
                    len(sentence),
                    sentence,
                )
            )

    scored.sort(
        key=lambda item: (
            item[0],
            -item[1],
        ),
        reverse=True,
    )

    selected = []

    seen = set()

    for _, _, sentence in scored:
        normalized = sentence.lower()

        if normalized in seen:
            continue

        seen.add(normalized)

        selected.append(sentence)

        if len(selected) >= max_sentences:
            break

    return selected


def build_evidence_cards(
    readable_sources: List[Dict],
) -> List[Dict]:
    """Build compact evidence cards."""

    cards = []

    for index, source in enumerate(
        readable_sources,
        start=1,
    ):
        evidence_sentences = extract_evidence_sentences(
            source["content"],
            RESEARCH_QUESTION,
        )

        evidence = " ".join(evidence_sentences)

        if not evidence:
            continue

        cards.append(
            {
                "id": index,
                "title": source["title"],
                "url": source["url"],
                "quality_category": source[
                    "quality_category"
                ],
                "quality_score": source[
                    "quality_score"
                ],
                "relevance_score": source[
                    "relevance_score"
                ],
                "evidence": evidence[:2200],
            }
        )

    return cards


# ============================================================
# CLAIM PARSING
# ============================================================

def clean_claim_text(claim: str) -> str:
    """Clean generated claim text."""

    claim = claim.strip()

    claim = re.sub(
        r"^\s*[-*\d\.\)\:]+\s*",
        "",
        claim,
    )

    claim = re.sub(
        r"^(CLAIM|Claim)\s*:\s*",
        "",
        claim,
        flags=re.IGNORECASE,
    )

    claim = re.sub(
        r"\s+",
        " ",
        claim,
    ).strip()

    return claim


def parse_claims_from_llm(
    content: str,
) -> List[Dict]:
    """
    Parse multiple possible LLM formats.

    Supported formats:

    CLAIM: text | SOURCES: 1,2

    CLAIM: text
    SOURCES: 1,2

    1. text | SOURCES: 1,2

    text [Sources: 1,2]
    """

    claims = []

    # --------------------------------------------------------
    # Format 1:
    # CLAIM: ... | SOURCES: ...
    # --------------------------------------------------------

    pattern = re.compile(
        r"CLAIM\s*:\s*(.*?)\s*\|\s*SOURCES?\s*:\s*([0-9,\s]+)",
        re.IGNORECASE,
    )

    for match in pattern.finditer(content):
        claim = clean_claim_text(match.group(1))

        source_numbers = [
            int(number)
            for number in re.findall(
                r"\d+",
                match.group(2),
            )
        ]

        if claim and source_numbers:
            claims.append(
                {
                    "claim": claim,
                    "sources": sorted(
                        set(source_numbers)
                    ),
                }
            )

    if claims:
        return claims[:MAX_CLAIMS]

    # --------------------------------------------------------
    # Format 2:
    # CLAIM line followed by SOURCES line
    # --------------------------------------------------------

    lines = [
        line.strip()
        for line in content.splitlines()
        if line.strip()
    ]

    current_claim = None

    for line in lines:

        if re.match(
            r"^CLAIM\s*:",
            line,
            re.IGNORECASE,
        ):
            current_claim = clean_claim_text(line)

        elif re.match(
            r"^SOURCES?\s*:",
            line,
            re.IGNORECASE,
        ):
            if current_claim:

                numbers = [
                    int(number)
                    for number in re.findall(
                        r"\d+",
                        line,
                    )
                ]

                if numbers:
                    claims.append(
                        {
                            "claim": current_claim,
                            "sources": sorted(
                                set(numbers)
                            ),
                        }
                    )

                    current_claim = None

    if claims:
        return claims[:MAX_CLAIMS]

    # --------------------------------------------------------
    # Format 3:
    # numbered claim + [Sources: 1,2]
    # --------------------------------------------------------

    for line in lines:

        source_match = re.search(
            r"\[?\s*SOURCES?\s*:\s*([0-9,\s]+)\s*\]?",
            line,
            re.IGNORECASE,
        )

        if not source_match:
            continue

        source_numbers = [
            int(number)
            for number in re.findall(
                r"\d+",
                source_match.group(1),
            )
        ]

        claim_part = re.sub(
            r"\[?\s*SOURCES?\s*:\s*[0-9,\s]+\s*\]?",
            "",
            line,
            flags=re.IGNORECASE,
        )

        claim_part = clean_claim_text(
            claim_part
        )

        if claim_part and source_numbers:
            claims.append(
                {
                    "claim": claim_part,
                    "sources": sorted(
                        set(source_numbers)
                    ),
                }
            )

    return claims[:MAX_CLAIMS]


# ============================================================
# DETERMINISTIC FALLBACK CLAIMS
# ============================================================

def generate_fallback_claims(
    evidence_cards: List[Dict],
) -> List[Dict]:
    """
    Generate claims without depending on LLM formatting.

    These claims are derived directly from evidence sentences.
    """

    logger.warning(
        "Using deterministic fallback claim generation."
    )

    candidates = []

    patterns = [
        (
            r"voice",
            "Voice-based AI technology can help provide agricultural information to farmers."
        ),
        (
            r"local language|regional language|multilingual",
            "AI-powered agricultural services can support communication in local or regional languages."
        ),
        (
            r"advisory",
            "AI-powered voice technology can support agricultural advisory services."
        ),
        (
            r"farmer|farmers",
            "AI-powered agricultural tools can provide information and assistance to farmers."
        ),
        (
            r"crop",
            "AI-based agricultural systems can support farmers with crop-related information."
        ),
        (
            r"weather",
            "AI-powered agricultural systems can provide weather-related information to farmers."
        ),
    ]

    for card in evidence_cards:

        evidence_lower = card["evidence"].lower()

        for pattern, fallback_claim in patterns:

            if re.search(
                pattern,
                evidence_lower,
            ):

                candidates.append(
                    {
                        "claim": fallback_claim,
                        "sources": [card["id"]],
                    }
                )

    # Deduplicate identical claims
    unique = []
    seen = set()

    for candidate in candidates:

        key = candidate["claim"].lower()

        if key in seen:
            continue

        seen.add(key)
        unique.append(candidate)

    return unique[:MAX_CLAIMS]


# ============================================================
# LLM CLAIM GENERATION
# ============================================================

def generate_claims(
    evidence_cards: List[Dict],
) -> List[Dict]:
    """Generate factual claims grounded in evidence cards."""

    evidence_text = []

    for card in evidence_cards:

        evidence_text.append(
            f"""
SOURCE {card['id']}
Title: {card['title']}
Quality: {card['quality_category']}
Evidence:
{card['evidence']}
"""
        )

    prompt = f"""
You are a strict evidence extraction assistant.

Research question:
{RESEARCH_QUESTION}

Use ONLY the evidence provided below.

Generate up to {MAX_CLAIMS} factual claims.

Every claim MUST be directly supported by one or more sources.

IMPORTANT:
Do not invent facts.
Do not add statistics unless explicitly present.
Do not make predictions.
Do not add information from your own knowledge.

Use EXACTLY this format:

CLAIM: factual statement | SOURCES: 1,2

Example:

CLAIM: Voice technology can provide agricultural advice to farmers. | SOURCES: 1
CLAIM: Agricultural services can support regional languages. | SOURCES: 1,2

Evidence:
{"".join(evidence_text)}
"""

    try:

        response = chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": 0,
            },
        )

        content = response["message"]["content"]

        claims = parse_claims_from_llm(
            content
        )

        # ----------------------------------------------------
        # Validate source IDs
        # ----------------------------------------------------

        valid_ids = {
            card["id"]
            for card in evidence_cards
        }

        validated = []

        for item in claims:

            valid_sources = [
                source_id
                for source_id in item["sources"]
                if source_id in valid_ids
            ]

            if not valid_sources:
                continue

            claim_text = clean_claim_text(
                item["claim"]
            )

            if len(claim_text) < 20:
                continue

            validated.append(
                {
                    "claim": claim_text,
                    "sources": sorted(
                        set(valid_sources)
                    ),
                }
            )

        if validated:

            logger.info(
                "Parsed %d evidence-mapped claims.",
                len(validated),
            )

            return validated[:MAX_CLAIMS]

        logger.warning(
            "LLM returned no valid evidence-mapped claims."
        )

    except Exception as exc:

        logger.warning(
            "LLM claim generation failed: %s",
            exc,
        )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    fallback_claims = generate_fallback_claims(
        evidence_cards
    )

    logger.info(
        "Fallback generated %d evidence-mapped claims.",
        len(fallback_claims),
    )

    return fallback_claims


# ============================================================
# TOKENIZATION
# ============================================================

STOPWORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "of",
    "to",
    "in",
    "for",
    "on",
    "with",
    "can",
    "be",
    "is",
    "are",
    "as",
    "by",
    "from",
    "that",
    "this",
    "these",
    "those",
    "it",
    "its",
    "their",
    "they",
    "them",
    "has",
    "have",
    "had",
    "will",
    "may",
    "such",
}


def meaningful_tokens(text: str) -> Set[str]:
    """Return meaningful tokens."""

    tokens = re.findall(
        r"[a-zA-Z]{3,}",
        text.lower(),
    )

    return {
        token
        for token in tokens
        if token not in STOPWORDS
    }


# ============================================================
# CLAIM-SPECIFIC EVIDENCE
# ============================================================

def get_claim_evidence(
    claim: Dict,
    evidence_cards: List[Dict],
) -> str:
    """Get evidence only from the sources mapped to a claim."""

    source_ids = set(
        claim["sources"]
    )

    evidence_parts = []

    for card in evidence_cards:

        if card["id"] not in source_ids:
            continue

        evidence_parts.append(
            f"SOURCE {card['id']}: {card['evidence']}"
        )

    return "\n".join(
        evidence_parts
    )


# ============================================================
# EVIDENCE OVERLAP
# ============================================================

def evidence_overlap(
    claim_text: str,
    evidence: str,
) -> float:
    """Calculate lexical overlap between claim and evidence."""

    claim_tokens = meaningful_tokens(
        claim_text
    )

    evidence_tokens = meaningful_tokens(
        evidence
    )

    if not claim_tokens:
        return 0.0

    overlap = claim_tokens.intersection(
        evidence_tokens
    )

    return len(overlap) / len(
        claim_tokens
    )


# ============================================================
# CLAIM DETAIL EXTRACTION
# ============================================================

def extract_claim_details(
    claim: str,
) -> List[str]:
    """
    Extract potentially important factual details.

    Used as a conservative heuristic.
    """

    details = []

    numbers = re.findall(
        r"\b\d+(?:\.\d+)?%?\b",
        claim,
    )

    details.extend(numbers)

    quoted = re.findall(
        r'"([^"]+)"',
        claim,
    )

    details.extend(quoted)

    return details


def unsupported_details(
    claim: str,
    evidence: str,
) -> List[str]:
    """Find important details not appearing in evidence."""

    details = extract_claim_details(
        claim
    )

    evidence_lower = evidence.lower()

    unsupported = []

    for detail in details:

        if detail.lower() not in evidence_lower:
            unsupported.append(detail)

    return unsupported


# ============================================================
# LLM VERIFICATION
# ============================================================

def verify_claim_with_llm(
    claim: str,
    evidence: str,
) -> Dict:
    """Ask LLM to verify one claim."""

    prompt = f"""
You are a strict fact checker.

Claim:
{claim}

Evidence:
{evidence}

Determine whether the evidence supports the claim.

Return EXACTLY:

VERDICT: SUPPORTED
REASON: short explanation

OR

VERDICT: PARTIALLY SUPPORTED
REASON: short explanation

OR

VERDICT: UNSUPPORTED
REASON: short explanation

Do not use outside knowledge.
"""

    try:

        response = chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            options={
                "temperature": 0,
            },
        )

        content = response["message"]["content"]

        verdict_match = re.search(
            r"VERDICT\s*:\s*(SUPPORTED|PARTIALLY SUPPORTED|UNSUPPORTED)",
            content,
            re.IGNORECASE,
        )

        reason_match = re.search(
            r"REASON\s*:\s*(.+)",
            content,
            re.IGNORECASE,
        )

        if verdict_match:

            verdict = (
                verdict_match.group(1)
                .upper()
                .strip()
            )

            reason = (
                reason_match.group(1).strip()
                if reason_match
                else "No reason provided."
            )

            return {
                "verdict": verdict,
                "reason": reason,
            }

    except Exception as exc:

        logger.warning(
            "Claim verification failed: %s",
            exc,
        )

    return {
        "verdict": "UNSUPPORTED",
        "reason": "Verification could not be completed.",
    }


# ============================================================
# MULTI-SOURCE AGREEMENT
# ============================================================

def calculate_multi_source_bonus(
    source_ids: List[int],
) -> int:
    """Reward claims supported by multiple sources."""

    unique_count = len(
        set(source_ids)
    )

    if unique_count >= 3:
        return 15

    if unique_count == 2:
        return 10

    if unique_count == 1:
        return 0

    return 0


# ============================================================
# STRICT FINAL VERDICT
# ============================================================

def calculate_final_verdict(
    llm_verdict: str,
    overlap: float,
    unsupported_details_list: List[str],
) -> str:
    """Calculate deterministic final verdict."""

    llm_verdict = llm_verdict.upper()

    # Unsupported factual details make the result conservative.
    if unsupported_details_list:
        if overlap < 0.55:
            return "UNSUPPORTED"

    # Strong evidence + LLM support
    if (
        overlap >= 0.55
        and llm_verdict == "SUPPORTED"
    ):
        return "SUPPORTED"

    # Moderate evidence
    if (
        overlap >= 0.35
        and llm_verdict in {
            "SUPPORTED",
            "PARTIALLY SUPPORTED",
        }
    ):
        return "PARTIALLY SUPPORTED"

    # Strong lexical evidence but LLM disagreement
    if (
        overlap >= 0.55
        and llm_verdict != "SUPPORTED"
    ):
        return "PARTIALLY SUPPORTED"

    # Very weak overlap
    if (
        llm_verdict == "SUPPORTED"
        and overlap < 0.35
    ):
        return "UNSUPPORTED"

    return "UNSUPPORTED"


# ============================================================
# CONFIDENCE SCORE
# ============================================================

def calculate_confidence_score(
    claim: Dict,
    evidence_cards: List[Dict],
    final_verdict: str,
    overlap: float,
) -> int:
    """Calculate deterministic confidence score."""

    source_quality_scores = []

    source_ids = set(
        claim["sources"]
    )

    for card in evidence_cards:

        if card["id"] in source_ids:

            source_quality_scores.append(
                card["quality_score"]
            )

    if source_quality_scores:
        max_quality = max(
            source_quality_scores
        )
    else:
        max_quality = 3

    # Convert 10-point source quality to 50-point component.
    quality_component = (
        max_quality * 5
    )

    # Verification component.
    if final_verdict == "SUPPORTED":
        support_component = 35
    elif final_verdict == "PARTIALLY SUPPORTED":
        support_component = 20
    else:
        support_component = 0

    # Multi-source component.
    multi_source_component = calculate_multi_source_bonus(
        claim["sources"]
    )

    # Relevance component.
    relevance_values = []

    for card in evidence_cards:

        if card["id"] in source_ids:
            relevance_values.append(
                card["relevance_score"]
            )

    if relevance_values:
        average_relevance = sum(
            relevance_values
        ) / len(relevance_values)
    else:
        average_relevance = 0

    relevance_component = min(
        10,
        int(average_relevance),
    )

    # Evidence overlap component.
    overlap_component = min(
        10,
        int(overlap * 10),
    )

    score = (
        quality_component
        + support_component
        + multi_source_component
        + relevance_component
        + overlap_component
    )

    # Conservative caps.
    if final_verdict == "UNSUPPORTED":
        score = min(score, 25)

    elif final_verdict == "PARTIALLY SUPPORTED":
        score = min(score, 65)

    return min(
        100,
        max(0, score),
    )


def confidence_level(score: int) -> str:
    """Convert numeric score into confidence level."""

    if score >= 80:
        return "HIGH"

    if score >= 60:
        return "MEDIUM"

    return "LOW"


# ============================================================
# FINAL REPORT
# ============================================================

def build_final_report(
    claims: List[Dict],
) -> str:
    """Create deterministic final report."""

    lines = []

    lines.append(
        "FINAL RESEARCH CONFIDENCE REPORT"
    )

    lines.append(
        "=" * 50
    )

    lines.append(
        f"Research Question: {RESEARCH_QUESTION}"
    )

    lines.append("")

    lines.append(
        f"Total verified claims: {len(claims)}"
    )

    lines.append("")

    verdict_counter = Counter(
        claim["final_verdict"]
        for claim in claims
    )

    lines.append(
        "VERDICT SUMMARY"
    )

    for verdict in [
        "SUPPORTED",
        "PARTIALLY SUPPORTED",
        "UNSUPPORTED",
    ]:

        lines.append(
            f"- {verdict}: "
            f"{verdict_counter.get(verdict, 0)}"
        )

    lines.append("")

    lines.append(
        "CLAIM DETAILS"
    )

    lines.append(
        "-" * 50
    )

    for index, claim in enumerate(
        claims,
        start=1,
    ):

        lines.append(
            f"\nClaim {index}: {claim['claim']}"
        )

        lines.append(
            f"Sources: {claim['sources']}"
        )

        lines.append(
            f"LLM Verdict: {claim['llm_verdict']}"
        )

        lines.append(
            f"Final Verdict: {claim['final_verdict']}"
        )

        lines.append(
            f"Evidence Overlap: "
            f"{claim['overlap']:.0%}"
        )

        lines.append(
            f"Confidence: "
            f"{claim['confidence_score']}/100 "
            f"({claim['confidence_level']})"
        )

        lines.append(
            f"Reason: {claim['verification_reason']}"
        )

    return "\n".join(lines)


# ============================================================
# MAIN
# ============================================================

def main() -> None:

    logger.info(
        "Starting Exercise 61.4.1 - Final Research Confidence System"
    )

    logger.info(
        "Research question: %s",
        RESEARCH_QUESTION,
    )

    # --------------------------------------------------------
    # STEP 1
    # --------------------------------------------------------

    logger.info(
        "Step 1: Generating research queries."
    )

    queries = generate_search_queries(
        RESEARCH_QUESTION
    )

    # --------------------------------------------------------
    # STEP 2
    # --------------------------------------------------------

    logger.info(
        "Step 2: Searching the web."
    )

    raw_results = []

    for query in queries:

        logger.info(
            "Searching: %s",
            query,
        )

        results = search_web(
            query
        )

        raw_results.extend(
            results
        )

    logger.info(
        "Collected %d raw search results.",
        len(raw_results),
    )

    # --------------------------------------------------------
    # STEP 3
    # --------------------------------------------------------

    logger.info(
        "Step 3: Deduplicating sources."
    )

    unique_sources = deduplicate_sources(
        raw_results
    )

    logger.info(
        "Unique sources after deduplication: %d",
        len(unique_sources),
    )

    # --------------------------------------------------------
    # STEP 4
    # --------------------------------------------------------

    logger.info(
        "Step 4: Filtering and ranking sources."
    )

    relevant_sources = rank_sources(
        unique_sources
    )

    logger.info(
        "Relevant sources after filtering: %d",
        len(relevant_sources),
    )

    candidate_sources = relevant_sources[
        :MAX_CANDIDATE_SOURCES
    ]

    logger.info(
        "Selected %d candidate sources.",
        len(candidate_sources),
    )

    # --------------------------------------------------------
    # STEP 5
    # --------------------------------------------------------

    logger.info(
        "Step 5: Fetching source content."
    )

    readable_sources = []

    for index, source in enumerate(
        candidate_sources,
        start=1,
    ):

        logger.info(
            "Fetching source %d/%d: %s",
            index,
            len(candidate_sources),
            source["title"],
        )

        content = fetch_source_content(
            source["url"]
        )

        if not content:

            logger.warning(
                "Source is not readable: %s",
                source["url"],
            )

            continue

        source["content"] = content

        readable_sources.append(
            source
        )

        if (
            len(readable_sources)
            >= MAX_READABLE_SOURCES
        ):
            break

    logger.info(
        "Readable evidence sources: %d",
        len(readable_sources),
    )

    if not readable_sources:

        logger.error(
            "No readable evidence sources found."
        )

        return

    # --------------------------------------------------------
    # EVIDENCE CARDS
    # --------------------------------------------------------

    logger.info(
        "Building compact evidence cards."
    )

    evidence_cards = build_evidence_cards(
        readable_sources
    )

    logger.info(
        "Created %d evidence cards.",
        len(evidence_cards),
    )

    if not evidence_cards:

        logger.error(
            "No evidence cards could be created."
        )

        return

    # --------------------------------------------------------
    # STEP 6
    # --------------------------------------------------------

    logger.info(
        "Step 6: Generating evidence-based claims."
    )

    claims = generate_claims(
        evidence_cards
    )

    logger.info(
        "Final claim count: %d",
        len(claims),
    )

    if not claims:

        logger.error(
            "No evidence-mapped claims generated."
        )

        return

    # --------------------------------------------------------
    # STEP 7
    # --------------------------------------------------------

    logger.info(
        "Step 7: Verifying each claim."
    )

    verified_claims = []

    for index, claim in enumerate(
        claims,
        start=1,
    ):

        logger.info(
            "Verifying claim %d/%d: %s",
            index,
            len(claims),
            claim["claim"],
        )

        evidence = get_claim_evidence(
            claim,
            evidence_cards,
        )

        overlap = evidence_overlap(
            claim["claim"],
            evidence,
        )

        unsupported_details_list = (
            unsupported_details(
                claim["claim"],
                evidence,
            )
        )

        llm_result = verify_claim_with_llm(
            claim["claim"],
            evidence,
        )

        final_verdict = calculate_final_verdict(
            llm_result["verdict"],
            overlap,
            unsupported_details_list,
        )

        confidence_score = calculate_confidence_score(
            claim,
            evidence_cards,
            final_verdict,
            overlap,
        )

        level = confidence_level(
            confidence_score
        )

        verified_claim = {
            **claim,
            "llm_verdict": llm_result[
                "verdict"
            ],
            "verification_reason": llm_result[
                "reason"
            ],
            "overlap": overlap,
            "unsupported_details": unsupported_details_list,
            "final_verdict": final_verdict,
            "confidence_score": confidence_score,
            "confidence_level": level,
        }

        verified_claims.append(
            verified_claim
        )

        logger.info(
            "Claim %d result: %s | Confidence: %d/100 (%s)",
            index,
            final_verdict,
            confidence_score,
            level,
        )

    # --------------------------------------------------------
    # STEP 8
    # --------------------------------------------------------

    logger.info(
        "Step 8: Building deterministic final report."
    )

    report = build_final_report(
        verified_claims
    )

    print("\n")
    print(report)

    logger.info(
        "Exercise 61.4.1 completed successfully."
    )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()