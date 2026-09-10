import logging

from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================
# LOGGER SETUP
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_data_analytics")

logger.info("Starting Data & Analytics exercise")


# ============================================================
# CREATE DATA ANALYTICS AGENT
# ============================================================

agent = Agent(
    name="GramSwaram Data Analytics Agent",

    model=Ollama(
        id="llama3.2"
    ),

    instructions=[
        "You are a data analytics assistant for GramSwaram.",
        "Analyze the farmer's production data carefully.",
        "Perform calculations accurately.",
        "Do not invent data.",
        "Clearly show important numerical results.",
        "Give a short and simple insight after the calculations.",
    ],
)

logger.info("Data Analytics Agent initialized")


# ============================================================
# FARMER PRODUCTION DATA
# ============================================================

production_data = {
    2023: 800,
    2024: 950,
    2025: 1100,
}

logger.info(
    "Production data loaded for %d years",
    len(production_data),
)


# ============================================================
# DISPLAY DATA
# ============================================================

print("=" * 60)
print("GRAMSWARAM DATA & ANALYTICS")
print("=" * 60)

print("\nFarmer Crop Production Data:")

for year, production in production_data.items():
    print(f"{year}: {production} kg")


# ============================================================
# ASK AGENT TO ANALYZE DATA
# ============================================================

analysis_prompt = f"""
Analyze the following turmeric crop production data.

Production data:

2023: {production_data[2023]} kg
2024: {production_data[2024]} kg
2025: {production_data[2025]} kg

Calculate and explain:

1. Total production across all three years.
2. Average annual production.
3. Highest production year.
4. Lowest production year.
5. Increase in production from 2023 to 2025.
6. Percentage increase from 2023 to 2025.
7. Give one short insight about the production trend.

Use the actual numbers from the data.
Do not invent any additional information.

Present the answer clearly.
"""


print("\n" + "=" * 60)
print("ANALYZING DATA")
print("=" * 60)

logger.info("Sending production data to analytics agent")


# ============================================================
# RUN AGENT
# ============================================================

try:

    response = agent.run(
        analysis_prompt
    )

    print("\nAnalytics Result:")
    print(response.content)

    logger.info(
        "Data analysis completed successfully"
    )

except Exception:

    logger.exception(
        "Data analysis failed"
    )

    raise


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 60)
print("DATA ANALYTICS EXERCISE COMPLETE")
print("=" * 60)

logger.info(
    "Data & Analytics exercise completed successfully"
)