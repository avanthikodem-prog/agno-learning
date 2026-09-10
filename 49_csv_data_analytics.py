import csv
import logging
from pathlib import Path

from agno.agent import Agent
from agno.models.ollama import Ollama


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_csv_analytics")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

CSV_FILE = Path("farmer_production.csv")


# ---------------------------------------------------------
# Read CSV data
# ---------------------------------------------------------

def load_production_data(file_path: Path) -> list[dict]:
    """Read farmer production data from CSV."""

    logger.info("Reading CSV file: %s", file_path)

    if not file_path.exists():
        logger.error("CSV file not found: %s", file_path)
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    with file_path.open("r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        data = []

        for row in reader:
            row["year"] = int(row["year"])
            row["production_kg"] = float(row["production_kg"])
            data.append(row)

    logger.info("Loaded %d records from CSV", len(data))

    return data


# ---------------------------------------------------------
# Analytics
# ---------------------------------------------------------

def analyze_production(data: list[dict]) -> dict:
    """Calculate basic production statistics."""

    logger.info("Starting production analysis")

    total_production = sum(
        row["production_kg"]
        for row in data
    )

    average_production = (
        total_production / len(data)
        if data
        else 0
    )

    crop_totals = {}

    for row in data:
        crop = row["crop"]

        crop_totals[crop] = (
            crop_totals.get(crop, 0)
            + row["production_kg"]
        )

    highest_crop = max(
        crop_totals,
        key=crop_totals.get
    )

    result = {
        "total_production_kg": total_production,
        "average_production_kg": average_production,
        "crop_totals": crop_totals,
        "highest_production_crop": highest_crop,
    }

    logger.info(
        "Total production: %.2f kg",
        total_production,
    )

    logger.info(
        "Average production per record: %.2f kg",
        average_production,
    )

    logger.info(
        "Highest production crop: %s",
        highest_crop,
    )

    return result


# ---------------------------------------------------------
# Agno Agent
# ---------------------------------------------------------

def create_agent() -> Agent:
    """Create the Agno analytics agent."""

    logger.info("Creating Agno analytics agent")

    agent = Agent(
        model=Ollama(id="llama3.2"),
        instructions=[
            "You are a farmer-friendly agricultural data analyst.",
            "Analyze the production data provided by the user.",
            "Explain results in simple language.",
            "Highlight important trends.",
            "Give practical insights.",
            "Do not invent data that is not provided.",
        ],
        markdown=True,
    )

    logger.info("Agno analytics agent created")

    return agent


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    logger.info("Starting CSV Data Analytics exercise")

    data = load_production_data(CSV_FILE)

    analysis = analyze_production(data)

    print("\n========== PRODUCTION DATA ==========\n")

    for row in data:
        print(
            f"{row['year']} | "
            f"{row['crop']} | "
            f"{row['production_kg']} kg"
        )

    print("\n========== ANALYTICS ==========\n")

    print(
        f"Total Production: "
        f"{analysis['total_production_kg']:.2f} kg"
    )

    print(
        f"Average Production: "
        f"{analysis['average_production_kg']:.2f} kg"
    )

    print(
        f"Highest Production Crop: "
        f"{analysis['highest_production_crop']}"
    )

    print("\nCrop-wise Production:")

    for crop, total in analysis["crop_totals"].items():
        print(f"{crop}: {total:.2f} kg")

    # -----------------------------------------------------
    # Ask Agno Agent for farmer-friendly insight
    # -----------------------------------------------------

    agent = create_agent()

    prompt = f"""
Analyze the following agricultural production data.

Raw data:
{data}

Calculated statistics:
{analysis}

Explain:
1. Which crop has the highest total production?
2. What is the total production?
3. What useful trend can be observed?
4. Give a simple farmer-friendly insight.

Do not invent any additional numbers.
"""

    logger.info("Sending analytics to Agno agent")

    response = agent.run(prompt)

    print("\n========== AGNO INSIGHTS ==========\n")

    print(response.content)

    logger.info("CSV Data Analytics exercise completed successfully")


if __name__ == "__main__":
    main()