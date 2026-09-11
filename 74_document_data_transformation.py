import logging
from pathlib import Path


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_document_data_transformation")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

DOCUMENT_PATH = BASE_DIR / "73_sample_data.txt"


# ---------------------------------------------------------
# Read document
# ---------------------------------------------------------
def read_document(file_path: Path) -> str:
    """Read the normalized sample document."""

    logger.info("Reading document: %s", file_path.name)

    if not file_path.exists():
        logger.error("Document not found: %s", file_path)
        raise FileNotFoundError(f"Document not found: {file_path}")

    text = file_path.read_text(encoding="utf-8")

    logger.info(
        "Document loaded successfully: %d characters",
        len(text),
    )

    return text


# ---------------------------------------------------------
# Parse and normalize table
# ---------------------------------------------------------
def parse_and_normalize_table(document: str) -> list[dict]:
    """Parse the table and normalize its values."""

    logger.info("Parsing and normalizing table data")

    lines = [
        line.strip()
        for line in document.splitlines()
        if "|" in line
    ]

    if not lines:
        raise ValueError("No table data found")

    parsed_rows = []

    for line in lines:
        columns = [
            column.strip()
            for column in line.split("|")
        ]

        parsed_rows.append(columns)

    headers = parsed_rows[0]
    raw_rows = parsed_rows[1:]

    rows = []

    for row in raw_rows:

        if len(row) != len(headers):
            logger.warning(
                "Skipping row with incorrect column count: %s",
                row,
            )
            continue

        product = row[0].strip().title()

        price = (
            row[1]
            .strip()
            .replace("₹", "")
            .replace(",", "")
            .replace(" ", "")
        )

        category = row[2].strip().title()

        availability = row[3].strip().lower()

        if availability == "available":
            availability = "Available"
        elif availability == "out of stock":
            availability = "Out of Stock"
        else:
            availability = availability.title()

        rows.append(
            {
                "Product": product,
                "Price": float(price),
                "Category": category,
                "Availability": availability,
            }
        )

    logger.info(
        "Successfully prepared %d normalized rows",
        len(rows),
    )

    return rows


# ---------------------------------------------------------
# Calculate basic statistics
# ---------------------------------------------------------
def calculate_statistics(rows: list[dict]) -> dict:
    """Calculate statistics from the product data."""

    logger.info("Calculating document data statistics")

    total_products = len(rows)

    total_price = sum(
        row["Price"]
        for row in rows
    )

    average_price = (
        total_price / total_products
        if total_products > 0
        else 0
    )

    available_products = [
        row
        for row in rows
        if row["Availability"] == "Available"
    ]

    out_of_stock_products = [
        row
        for row in rows
        if row["Availability"] == "Out of Stock"
    ]

    agriculture_products = [
        row
        for row in rows
        if row["Category"] == "Agriculture"
    ]

    grocery_products = [
        row
        for row in rows
        if row["Category"] == "Grocery"
    ]

    statistics = {
        "total_products": total_products,
        "total_price": total_price,
        "average_price": average_price,
        "available_count": len(available_products),
        "out_of_stock_count": len(out_of_stock_products),
        "agriculture_count": len(agriculture_products),
        "grocery_count": len(grocery_products),
    }

    logger.info(
        "Statistics calculated successfully"
    )

    return statistics


# ---------------------------------------------------------
# Find highest priced product
# ---------------------------------------------------------
def find_highest_priced_product(rows: list[dict]) -> dict:
    """Find the product with the highest price."""

    logger.info("Finding highest priced product")

    if not rows:
        return {}

    product = max(
        rows,
        key=lambda row: row["Price"],
    )

    logger.info(
        "Highest priced product: %s",
        product["Product"],
    )

    return product


# ---------------------------------------------------------
# Find lowest priced product
# ---------------------------------------------------------
def find_lowest_priced_product(rows: list[dict]) -> dict:
    """Find the product with the lowest price."""

    logger.info("Finding lowest priced product")

    if not rows:
        return {}

    product = min(
        rows,
        key=lambda row: row["Price"],
    )

    logger.info(
        "Lowest priced product: %s",
        product["Product"],
    )

    return product


# ---------------------------------------------------------
# Group products by category
# ---------------------------------------------------------
def group_by_category(rows: list[dict]) -> dict:
    """Group products by category."""

    logger.info("Grouping products by category")

    grouped = {}

    for row in rows:
        category = row["Category"]

        if category not in grouped:
            grouped[category] = []

        grouped[category].append(row["Product"])

    logger.info(
        "Created %d product categories",
        len(grouped),
    )

    return grouped


# ---------------------------------------------------------
# Display transformation report
# ---------------------------------------------------------
def display_report(
    rows: list[dict],
    statistics: dict,
    highest_product: dict,
    lowest_product: dict,
    grouped_products: dict,
) -> None:
    """Display the transformed data report."""

    print("\n" + "=" * 70)
    print("DOCUMENT DATA TRANSFORMATION REPORT")
    print("=" * 70)

    print("\nPRODUCT SUMMARY")
    print("-" * 70)

    print(
        f"Total Products        : "
        f"{statistics['total_products']}"
    )

    print(
        f"Total Product Value   : "
        f"₹{statistics['total_price']:.2f}"
    )

    print(
        f"Average Product Price : "
        f"₹{statistics['average_price']:.2f}"
    )

    print(
        f"Available Products    : "
        f"{statistics['available_count']}"
    )

    print(
        f"Out of Stock Products : "
        f"{statistics['out_of_stock_count']}"
    )

    print(
        f"Agriculture Products  : "
        f"{statistics['agriculture_count']}"
    )

    print(
        f"Grocery Products      : "
        f"{statistics['grocery_count']}"
    )

    print("\nPRICE ANALYSIS")
    print("-" * 70)

    print(
        f"Highest Priced Product : "
        f"{highest_product['Product']} "
        f"(₹{highest_product['Price']:.2f})"
    )

    print(
        f"Lowest Priced Product  : "
        f"{lowest_product['Product']} "
        f"(₹{lowest_product['Price']:.2f})"
    )

    print("\nPRODUCTS BY CATEGORY")
    print("-" * 70)

    for category, products in grouped_products.items():

        print(f"\n{category}:")

        for product in products:
            print(f"  - {product}")

    print("\n" + "=" * 70)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    logger.info(
        "Starting Exercise 74 - Document Data Transformation"
    )

    # Step 1: Read document
    document = read_document(DOCUMENT_PATH)

    # Step 2: Parse and normalize
    rows = parse_and_normalize_table(document)

    # Step 3: Calculate statistics
    statistics = calculate_statistics(rows)

    # Step 4: Find highest priced product
    highest_product = find_highest_priced_product(rows)

    # Step 5: Find lowest priced product
    lowest_product = find_lowest_priced_product(rows)

    # Step 6: Group products by category
    grouped_products = group_by_category(rows)

    # Step 7: Display final report
    display_report(
        rows,
        statistics,
        highest_product,
        lowest_product,
        grouped_products,
    )

    print("\nExercise 74 completed successfully.")

    logger.info(
        "Exercise 74 completed successfully"
    )


if __name__ == "__main__":
    main()