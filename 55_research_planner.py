"""
Exercise 55 - Research Planning Agent

Architecture:

Research Question
        ↓
Agno Research Planner
        ↓
Research Sub-Questions
        ↓
Search Queries
        ↓
DDGS Web Search
        ↓
Collect Sources
        ↓
Agno + Ollama
        ↓
Research Plan + Initial Evidence
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

logger = logging.getLogger("gram_swaram_research_planner")


# ============================================================
# 2. CREATE RESEARCH PLANNER
# ============================================================

def create_planner() -> Agent:
    """Create an Agno agent that creates a research plan."""

    logger.info("Creating research planning agent.")

    agent = Agent(
        model=Ollama(id="llama3.2"),

        instructions=[
            "You are an expert research planning assistant.",
            "Break complex research questions into smaller research areas.",
            "Create focused research sub-questions.",
            "Create useful web search queries.",
            "Avoid duplicate or overlapping queries.",
            "Keep the plan practical and easy to execute.",
            "Do not answer the research question yet.",
        ],

        markdown=True,
    )

    logger.info(
        "Research planning agent created successfully."
    )

    return agent


# ============================================================
# 3. GENERATE RESEARCH PLAN
# ============================================================

def generate_research_plan(
    research_question: str,
) -> str:
    """Generate a structured research plan."""

    logger.info(
        "Generating research plan for: %s",
        research_question,
    )

    planner = create_planner()

    prompt = f"""
Create a research plan for the following question:

{research_question}


Use this exact structure:


# Research Plan

## 1. Research Goal

Explain what the research should discover.

## 2. Research Areas

Identify the major areas that need investigation.

## 3. Research Sub-Questions

Create 5 to 7 focused sub-questions.

## 4. Web Search Queries

Create one or two useful search queries for each
important research area.

## 5. Expected Evidence

Explain what type of evidence should be collected.

## 6. Research Risks

Identify possible problems such as:

- biased sources
- outdated information
- unsupported claims
- conflicting information
- insufficient evidence


IMPORTANT:

Do not answer the research question.

Only create the research plan.
"""

    try:

        logger.info(
            "Sending planning request to Ollama."
        )

        response = planner.run(prompt)

        plan = response.content

        logger.info(
            "Research plan generated successfully. Characters: %d",
            len(plan),
        )

        return plan

    except Exception as exc:

        logger.exception(
            "Research planning failed: %s",
            exc,
        )

        return "Research planning failed."


# ============================================================
# 4. WEB SEARCH
# ============================================================

def search_web(
    query: str,
    max_results: int = 4,
) -> list[dict]:
    """Search the web using DDGS."""

    logger.info(
        "Searching web for: %s",
        query,
    )

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
                        "title": result.get(
                            "title",
                            "",
                        ),
                        "url": result.get(
                            "href",
                            "",
                        ),
                        "snippet": result.get(
                            "body",
                            "",
                        ),
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
# 5. EXECUTE RESEARCH SEARCHES
# ============================================================

def execute_searches() -> list[dict]:
    """
    Execute planned research queries.

    For this exercise, the queries are based on the
    research plan generated for our agriculture topic.
    """

    logger.info(
        "Starting planned research searches."
    )

    queries = [
        "AI agents agriculture farmer advisory use cases",
        "AI agents agriculture crop monitoring decision support",
        "AI voice assistants farmers India agriculture",
        "AI agents agriculture benefits productivity sustainability",
        "AI agriculture risks reliability hallucination safety",
        "AI agriculture data privacy infrastructure challenges",
    ]

    all_sources = []

    for query in queries:

        results = search_web(
            query=query,
            max_results=4,
        )

        all_sources.extend(results)

    logger.info(
        "Planned research completed. Raw sources: %d",
        len(all_sources),
    )

    return all_sources


# ============================================================
# 6. DEDUPLICATE SOURCES
# ============================================================

def deduplicate_sources(
    sources: list[dict],
) -> list[dict]:
    """Remove duplicate URLs."""

    logger.info(
        "Starting source deduplication. Input: %d",
        len(sources),
    )

    unique_sources = []
    seen_urls = set()

    for source in sources:

        url = source.get(
            "url",
            "",
        ).strip()

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
# 7. BUILD EVIDENCE SUMMARY
# ============================================================

def build_evidence(
    sources: list[dict],
) -> str:
    """Prepare collected sources as evidence."""

    logger.info(
        "Building evidence from %d sources.",
        len(sources),
    )

    evidence = []

    for index, source in enumerate(
        sources,
        start=1,
    ):

        evidence.append(
            f"""
SOURCE {index}

Title:
{source.get("title", "Unknown")}

URL:
{source.get("url", "Unknown")}

Evidence:
{source.get("snippet", "No evidence available")}

----------------------------------------
"""
        )

    combined = "\n".join(evidence)

    logger.info(
        "Evidence prepared. Characters: %d",
        len(combined),
    )

    return combined


# ============================================================
# 8. GENERATE RESEARCH SUMMARY
# ============================================================

def generate_research_summary(
    research_question: str,
    research_plan: str,
    sources: list[dict],
) -> str:
    """Generate an initial research summary."""

    logger.info(
        "Creating final research synthesis agent."
    )

    agent = Agent(
        model=Ollama(id="llama3.2"),

        instructions=[
            "You are a research synthesis assistant.",
            "Use only the supplied research evidence.",
            "Do not invent facts.",
            "Do not invent URLs.",
            "Do not invent statistics.",
            "Clearly identify evidence limitations.",
            "Separate findings from assumptions.",
        ],

        markdown=True,
    )

    evidence = build_evidence(sources)

    prompt = f"""
Research Question:

{research_question}


Research Plan:

{research_plan}


Collected Evidence:

{evidence}


Create an initial research synthesis using this structure:


# Initial Research Synthesis

## 1. Research Question

State the research question.

## 2. Main Findings

List the most important findings.

## 3. Findings by Research Area

Group findings according to the research areas.

## 4. Supporting Sources

For important findings, mention the source number.

## 5. Evidence Gaps

Explain what the collected evidence does not establish.

## 6. Conflicting Information

Identify any conflicts between sources.

## 7. Preliminary Conclusion

Give a cautious conclusion based only on the evidence.


IMPORTANT:

- Do not invent information.
- Do not invent URLs.
- Do not invent statistics.
- Do not treat search snippets as complete articles.
- If evidence is insufficient, explicitly say so.
"""


    try:

        logger.info(
            "Sending collected evidence to Ollama."
        )

        response = agent.run(prompt)

        summary = response.content

        logger.info(
            "Research synthesis generated successfully. Characters: %d",
            len(summary),
        )

        return summary

    except Exception as exc:

        logger.exception(
            "Research synthesis failed: %s",
            exc,
        )

        return "Research synthesis failed."


# ============================================================
# 9. MAIN
# ============================================================

def main() -> None:
    """Main application entry point."""

    logger.info(
        "Starting Exercise 55 - Research Planning Agent."
    )

    research_question = (
        "How can AI agents be used in agriculture and farmer "
        "services, and what are the major opportunities, "
        "evidence, and challenges?"
    )

    logger.info(
        "Research question: %s",
        research_question,
    )

    # --------------------------------------------------------
    # Step 1: Create research plan
    # --------------------------------------------------------

    research_plan = generate_research_plan(
        research_question
    )

    print("\n")
    print("=" * 80)
    print("GRAM SWARAM - RESEARCH PLAN")
    print("=" * 80)

    print(research_plan)

    # --------------------------------------------------------
    # Step 2: Execute research
    # --------------------------------------------------------

    raw_sources = execute_searches()

    if not raw_sources:

        logger.error(
            "No sources were collected."
        )

        print("\nNo research sources were collected.")

        return

    # --------------------------------------------------------
    # Step 3: Deduplicate
    # --------------------------------------------------------

    sources = deduplicate_sources(
        raw_sources
    )

    # --------------------------------------------------------
    # Step 4: Limit evidence
    # --------------------------------------------------------

    sources = sources[:12]

    logger.info(
        "Final evidence sources selected: %d",
        len(sources),
    )

    # --------------------------------------------------------
    # Step 5: Generate synthesis
    # --------------------------------------------------------

    summary = generate_research_summary(
        research_question=research_question,
        research_plan=research_plan,
        sources=sources,
    )

    # --------------------------------------------------------
    # Step 6: Display synthesis
    # --------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("GRAM SWARAM - INITIAL RESEARCH SYNTHESIS")
    print("=" * 80)

    print(summary)

    # --------------------------------------------------------
    # Step 7: Display sources
    # --------------------------------------------------------

    print("\n")
    print("=" * 80)
    print("RESEARCH SOURCES")
    print("=" * 80)

    for index, source in enumerate(
        sources,
        start=1,
    ):

        print(
            f"\n[{index}] {source['title']}"
        )

        print(
            source["url"]
        )

    logger.info(
        "Exercise 55 completed successfully."
    )


# ============================================================
# 10. RUN
# ============================================================

if __name__ == "__main__":
    main()