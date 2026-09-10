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

logger = logging.getLogger("gram_swaram_advanced_analytics")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

CSV_FILE = Path("farmer_production.csv")


# ---------------------------------------------------------
# Load CSV data
# ---------------------------------------------------------

def load_production_data(file_path: Path) -> list[dict]:
    """Load agricultural production data from CSV."""

    logger.info("Reading CSV file: %s", file_path)

    if not file_path.exists():
        logger.error("CSV file not found: %s", file_path)
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    with file_path.open(
        "r",
        encoding="utf-8",
        newline="",
    ) as file:

        reader = csv.DictReader(file)

        data = []

        for row in reader:
            row["year"] = int(row["year"])
            row["production_kg"] = float(row["production_kg"])

            data.append(row)

    logger.info(
        "Loaded %d production records",
        len(data),
    )

    return data


# ---------------------------------------------------------
# Year-wise analysis
# ---------------------------------------------------------

def calculate_yearly_production(data: list[dict]) -> dict:
    """Calculate total production for each year."""

    logger.info("Calculating year-wise production")

    yearly_production = {}

    for row in data:
        year = row["year"]
        production = row["production_kg"]

        yearly_production[year] = (
            yearly_production.get(year, 0)
            + production
        )

    logger.info(
        "Year-wise production calculated: %s",
        yearly_production,
    )

    return yearly_production


# ---------------------------------------------------------
# Crop-wise analysis
# ---------------------------------------------------------

def calculate_crop_production(data: list[dict]) -> dict:
    """Calculate total production for each crop."""

    logger.info("Calculating crop-wise production")

    crop_production = {}

    for row in data:
        crop = row["crop"]
        production = row["production_kg"]

        crop_production[crop] = (
            crop_production.get(crop, 0)
            + production
        )

    logger.info(
        "Crop-wise production calculated: %s",
        crop_production,
    )

    return crop_production


# ---------------------------------------------------------
# Growth calculation
# ---------------------------------------------------------

def calculate_growth_percentage(yearly_production: dict) -> float:
    """Calculate production growth from first year to last year."""

    logger.info("Calculating production growth percentage")

    years = sorted(yearly_production.keys())

    if len(years) < 2:
        logger.warning(
            "Not enough years available to calculate growth"
        )
        return 0.0

    first_year = years[0]
    last_year = years[-1]

    first_value = yearly_production[first_year]
    last_value = yearly_production[last_year]

    if first_value == 0:
        logger.warning(
            "First year's production is zero"
        )
        return 0.0

    growth = (
        (last_value - first_value)
        / first_value
    ) * 100

    logger.info(
        "Production growth from %s to %s: %.2f%%",
        first_year,
        last_year,
        growth,
    )

    return growth


# ---------------------------------------------------------
# Find best-performing year and crop
# ---------------------------------------------------------

def find_best_performers(
    yearly_production: dict,
    crop_production: dict,
) -> tuple[int, str]:
    """Find the year and crop with the highest production."""

    logger.info("Finding best-performing year and crop")

    best_year = max(
        yearly_production,
        key=yearly_production.get,
    )

    best_crop = max(
        crop_production,
        key=crop_production.get,
    )

    logger.info(
        "Best year: %s | Best crop: %s",
        best_year,
        best_crop,
    )

    return best_year, best_crop


# ---------------------------------------------------------
# Advanced analytics
# ---------------------------------------------------------

def perform_advanced_analysis(data: list[dict]) -> dict:
    """Perform complete advanced agricultural analysis."""

    logger.info("Starting advanced data analysis")

    yearly_production = calculate_yearly_production(data)

    crop_production = calculate_crop_production(data)

    growth_percentage = calculate_growth_percentage(
        yearly_production
    )

    best_year, best_crop = find_best_performers(
        yearly_production,
        crop_production,
    )

    analysis = {
        "yearly_production": yearly_production,
        "crop_production": crop_production,
        "growth_percentage": growth_percentage,
        "best_year": best_year,
        "best_crop": best_crop,
    }

    logger.info("Advanced analysis completed")

    return analysis


# ---------------------------------------------------------
# Agno Agent
# ---------------------------------------------------------

def create_agent() -> Agent:
    """Create an Agno agricultural analytics agent."""

    logger.info("Creating Agno advanced analytics agent")

    agent = Agent(
        model=Ollama(id="llama3.2"),
        instructions=[
            "You are an agricultural data analyst.",
            "Analyze the provided agricultural statistics.",
            "Explain the results in simple farmer-friendly language.",
            "Identify important production trends.",
            "Explain production growth.",
            "Mention the best-performing year and crop.",
            "Give practical recommendations.",
            "Only use the data provided.",
            "Never invent statistics.",
        ],
        markdown=True,
    )

    logger.info(
        "Agno advanced analytics agent created"
    )

    return agent


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    logger.info(
        "Starting Advanced Data Analytics exercise"
    )

    # Load CSV
    data = load_production_data(CSV_FILE)

    # Perform analytics
    analysis = perform_advanced_analysis(data)

    # -----------------------------------------------------
    # Display results
    # -----------------------------------------------------

    print("\n========== YEAR-WISE PRODUCTION ==========\n")

    for year, production in analysis[
        "yearly_production"
    ].items():

        print(
            f"{year}: "
            f"{production:.2f} kg"
        )

    print("\n========== CROP-WISE PRODUCTION ==========\n")

    for crop, production in analysis[
        "crop_production"
    ].items():

        print(
            f"{crop}: "
            f"{production:.2f} kg"
        )

    print("\n========== ADVANCED ANALYTICS ==========\n")

    print(
        f"Production Growth: "
        f"{analysis['growth_percentage']:.2f}%"
    )

    print(
        f"Best Production Year: "
        f"{analysis['best_year']}"
    )

    print(
        f"Best Performing Crop: "
        f"{analysis['best_crop']}"
    )

    # -----------------------------------------------------
    # Agno Agent
    # -----------------------------------------------------

    agent = create_agent()

    prompt = f"""
Analyze the following agricultural production statistics.

Year-wise production:
{analysis["yearly_production"]}

Crop-wise production:
{analysis["crop_production"]}

Production growth:
{analysis["growth_percentage"]:.2f}%

Best production year:
{analysis["best_year"]}

Best-performing crop:
{analysis["best_crop"]}

Provide a farmer-friendly report containing:

1. Overall production trend
2. Production growth explanation
3. Best-performing year
4. Best-performing crop
5. Important observation
6. Two practical recommendations

Use simple language.

Do not invent any numbers or information.
"""

    logger.info(
        "Sending advanced analytics to Agno agent"
    )

    response = agent.run(prompt)

    print("\n========== AGNO FARMER INSIGHTS ==========\n")

    print(response.content)

    logger.info(
        "Advanced Data Analytics exercise completed successfully"
    )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()