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

logger = logging.getLogger("gram_swaram_document_pipeline")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

DOCUMENT_PATH = BASE_DIR / "73_sample_data.txt"
OUTPUT_PATH = BASE_DIR / "76_pipeline_output.json"


# ---------------------------------------------------------
# Step 1: Read document
# ---------------------------------------------------------
def read_document(file_path: Path) -> str:
    """Read the source document."""

    logger.info("Reading document: %s", file_path.name)

    if not file_path.exists():
        logger.error("Document not found: %s", file_path)
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    document = file_path.read_text(
        encoding="utf-8"
    )

    logger.info(
        "Document loaded successfully: %d characters",
        len(document),
    )

    return document


# ---------------------------------------------------------
# Step 2: Extract table
# ---------------------------------------------------------
def extract_table(document: str) -> list[list[str]]:
    """Extract pipe-separated table rows."""

    logger.info("Extracting table data")

    lines = [
        line.strip()
        for line in document.splitlines()
        if "|" in line
    ]

    if not lines:
        logger.error("No table found")
        raise ValueError("No table data found")

    rows = []

    for line in lines:
        columns = [
            column.strip()
            for column in line.split("|")
        ]

        rows.append(columns)

    logger.info(
        "Table extraction completed: %d rows",
        len(rows) - 1,
    )

    return rows


# ---------------------------------------------------------
# Step 3: Validate table
# ---------------------------------------------------------
def validate_table(
    rows: list[list[str]],
) -> bool:
    """Validate extracted table."""

    logger.info("Validating table data")

    headers = rows[0]
    required_columns = [
        "Product",
        "Price",
        "Category",
        "Availability",
    ]

    for column in required_columns:
        if column not in headers:
            logger.error(
                "Missing required column: %s",
                column,
            )
            return False

    expected_column_count = len(headers)

    for row in rows[1:]:
        if len(row) != expected_column_count:
            logger.error(
                "Invalid row detected: %s",
                row,
            )
            return False

    logger.info("Table validation completed successfully")

    return True


# ---------------------------------------------------------
# Step 4: Normalize data
# ---------------------------------------------------------
def normalize_data(
    rows: list[list[str]],
) -> list[dict]:
    """Normalize product data."""

    logger.info("Normalizing product data")

    headers = rows[0]

    products = []

    for row in rows[1:]:

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
        "Normalization completed: %d products",
        len(products),
    )

    return products


# ---------------------------------------------------------
# Step 5: Transform data
# ---------------------------------------------------------
def transform_data(
    products: list[dict],
) -> dict:
    """Create analytical summary."""

    logger.info("Transforming product data")

    total_products = len(products)

    total_value = sum(
        product["price"]
        for product in products
    )

    average_price = (
        total_value / total_products
        if total_products
        else 0
    )

    available_products = sum(
        1
        for product in products
        if product["availability"] == "Available"
    )

    out_of_stock_products = sum(
        1
        for product in products
        if product["availability"] == "Out of Stock"
    )

    agriculture_products = sum(
        1
        for product in products
        if product["category"] == "Agriculture"
    )

    grocery_products = sum(
        1
        for product in products
        if product["category"] == "Grocery"
    )

    highest_product = max(
        products,
        key=lambda product: product["price"],
    )

    lowest_product = min(
        products,
        key=lambda product: product["price"],
    )

    summary = {
        "total_products": total_products,
        "total_value": total_value,
        "average_price": average_price,
        "available_products": available_products,
        "out_of_stock_products": out_of_stock_products,
        "agriculture_products": agriculture_products,
        "grocery_products": grocery_products,
        "highest_priced_product": {
            "product": highest_product["product"],
            "price": highest_product["price"],
        },
        "lowest_priced_product": {
            "product": lowest_product["product"],
            "price": lowest_product["price"],
        },
    }

    logger.info("Data transformation completed")

    return summary


# ---------------------------------------------------------
# Step 6: Export pipeline result
# ---------------------------------------------------------
def export_pipeline_result(
    products: list[dict],
    summary: dict,
    output_path: Path,
) -> None:
    """Export complete pipeline result."""

    logger.info(
        "Exporting pipeline result to: %s",
        output_path.name,
    )

    output_data = {
        "pipeline": "GramSwaram Document Processing Pipeline",
        "source_document": DOCUMENT_PATH.name,
        "products": products,
        "summary": summary,
        "status": "SUCCESS",
    }

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            output_data,
            file,
            indent=4,
            ensure_ascii=False,
        )

    logger.info(
        "Pipeline result exported successfully"
    )


# ---------------------------------------------------------
# Step 7: Display final report
# ---------------------------------------------------------
def display_report(
    products: list[dict],
    summary: dict,
) -> None:
    """Display final pipeline report."""

    print("\n" + "=" * 70)
    print("GRAMSWARAM DOCUMENT PROCESSING PIPELINE")
    print("=" * 70)

    print("\nPIPELINE STATUS")
    print("-" * 70)
    print("Extraction       : SUCCESS")
    print("Validation       : SUCCESS")
    print("Normalization    : SUCCESS")
    print("Transformation   : SUCCESS")
    print("Export            : SUCCESS")

    print("\nPRODUCT SUMMARY")
    print("-" * 70)

    print(
        f"Total Products          : "
        f"{summary['total_products']}"
    )

    print(
        f"Total Product Value     : "
        f"₹{summary['total_value']:.2f}"
    )

    print(
        f"Average Product Price  : "
        f"₹{summary['average_price']:.2f}"
    )

    print(
        f"Available Products      : "
        f"{summary['available_products']}"
    )

    print(
        f"Out of Stock Products   : "
        f"{summary['out_of_stock_products']}"
    )

    print(
        f"Agriculture Products    : "
        f"{summary['agriculture_products']}"
    )

    print(
        f"Grocery Products        : "
        f"{summary['grocery_products']}"
    )

    print(
        f"Highest Priced Product  : "
        f"{summary['highest_priced_product']['product']} "
        f"(₹{summary['highest_priced_product']['price']:.2f})"
    )

    print(
        f"Lowest Priced Product   : "
        f"{summary['lowest_priced_product']['product']} "
        f"(₹{summary['lowest_priced_product']['price']:.2f})"
    )

    print("\nPRODUCTS")
    print("-" * 70)

    for product in products:
        print(
            f"{product['product']:<15} | "
            f"₹{product['price']:<8.2f} | "
            f"{product['category']:<12} | "
            f"{product['availability']}"
        )

    print("\n" + "=" * 70)
    print("Exercise 76 completed successfully.")
    print("=" * 70)


# ---------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------
def main() -> None:
    logger.info(
        "Starting Exercise 76 - "
        "Document Processing Pipeline"
    )

    try:
        # 1. Read
        document = read_document(
            DOCUMENT_PATH
        )

        # 2. Extract
        rows = extract_table(document)

        # 3. Validate
        is_valid = validate_table(rows)

        if not is_valid:
            raise ValueError(
                "Document validation failed"
            )

        # 4. Normalize
        products = normalize_data(rows)

        # 5. Transform
        summary = transform_data(products)

        # 6. Export
        export_pipeline_result(
            products,
            summary,
            OUTPUT_PATH,
        )

        # 7. Report
        display_report(
            products,
            summary,
        )

        logger.info(
            "Exercise 76 completed successfully"
        )

    except Exception:
        logger.exception(
            "Document processing pipeline failed"
        )
        raise


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
if __name__ == "__main__":
    main()