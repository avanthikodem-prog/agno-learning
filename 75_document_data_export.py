import json
import logging
from pathlib import Path


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_document_data_export")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

DOCUMENT_PATH = BASE_DIR / "73_sample_data.txt"
OUTPUT_PATH = BASE_DIR / "75_products.json"


# ---------------------------------------------------------
# Read document
# ---------------------------------------------------------
def read_document(file_path: Path) -> str:
    """Read the source document."""

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
def parse_table(document: str) -> list[dict]:
    """Parse and normalize the product table."""

    logger.info("Parsing and normalizing table")

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

    products = []

    for row in raw_rows:

        if len(row) != len(headers):
            logger.warning(
                "Skipping invalid row: %s",
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

        products.append(
            {
                "product": product,
                "price": float(price),
                "category": category,
                "availability": availability,
            }
        )

    logger.info(
        "Prepared %d products for export",
        len(products),
    )

    return products


# ---------------------------------------------------------
# Create summary
# ---------------------------------------------------------
def create_summary(products: list[dict]) -> dict:
    """Create summary statistics."""

    logger.info("Creating product summary")

    total_products = len(products)

    total_value = sum(
        product["price"]
        for product in products
    )

    available_count = sum(
        1
        for product in products
        if product["availability"] == "Available"
    )

    out_of_stock_count = sum(
        1
        for product in products
        if product["availability"] == "Out of Stock"
    )

    agriculture_count = sum(
        1
        for product in products
        if product["category"] == "Agriculture"
    )

    grocery_count = sum(
        1
        for product in products
        if product["category"] == "Grocery"
    )

    average_price = (
        total_value / total_products
        if total_products
        else 0
    )

    summary = {
        "total_products": total_products,
        "total_value": total_value,
        "average_price": average_price,
        "available_products": available_count,
        "out_of_stock_products": out_of_stock_count,
        "agriculture_products": agriculture_count,
        "grocery_products": grocery_count,
    }

    logger.info("Product summary created")

    return summary


# ---------------------------------------------------------
# Export data to JSON
# ---------------------------------------------------------
def export_to_json(
    products: list[dict],
    summary: dict,
    output_path: Path,
) -> None:
    """Export products and summary to JSON."""

    logger.info(
        "Exporting data to: %s",
        output_path.name,
    )

    export_data = {
        "document": "GramSwaram Product Catalog",
        "products": products,
        "summary": summary,
    }

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            export_data,
            file,
            indent=4,
            ensure_ascii=False,
        )

    logger.info(
        "JSON export completed successfully"
    )


# ---------------------------------------------------------
# Display exported data
# ---------------------------------------------------------
def display_exported_data(output_path: Path) -> None:
    """Display the generated JSON file."""

    logger.info(
        "Reading exported JSON file"
    )

    content = output_path.read_text(
        encoding="utf-8"
    )

    print("\n" + "=" * 70)
    print("EXPORTED JSON DATA")
    print("=" * 70)

    print(content)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    logger.info(
        "Starting Exercise 75 - Document Data Export"
    )

    # Step 1: Read source document
    document = read_document(DOCUMENT_PATH)

    # Step 2: Parse and normalize
    products = parse_table(document)

    # Step 3: Create summary
    summary = create_summary(products)

    # Step 4: Export to JSON
    export_to_json(
        products,
        summary,
        OUTPUT_PATH,
    )

    # Step 5: Display exported file
    display_exported_data(OUTPUT_PATH)

    print("\n" + "=" * 70)
    print("Exercise 75 completed successfully.")
    print("=" * 70)

    print(
        f"\nJSON file created:"
        f"\n{OUTPUT_PATH}"
    )

    logger.info(
        "Exercise 75 completed successfully"
    )


if __name__ == "__main__":
    main()