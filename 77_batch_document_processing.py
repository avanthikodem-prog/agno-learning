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

logger = logging.getLogger("gram_swaram_batch_document_processing")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

INPUT_DOCUMENTS = [
    BASE_DIR / "77_product_catalog_1.txt",
    BASE_DIR / "77_product_catalog_2.txt",
]

OUTPUT_PATH = BASE_DIR / "77_batch_pipeline_output.json"


# ---------------------------------------------------------
# Read document
# ---------------------------------------------------------
def read_document(file_path: Path) -> str:
    """Read one document."""

    logger.info(
        "Reading document: %s",
        file_path.name,
    )

    if not file_path.exists():
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    document = file_path.read_text(
        encoding="utf-8"
    )

    logger.info(
        "Loaded %s characters from %s",
        len(document),
        file_path.name,
    )

    return document


# ---------------------------------------------------------
# Extract table
# ---------------------------------------------------------
def extract_table(document: str) -> list[list[str]]:
    """Extract pipe-separated table."""

    lines = [
        line.strip()
        for line in document.splitlines()
        if "|" in line
    ]

    if not lines:
        raise ValueError(
            "No table data found"
        )

    rows = []

    for line in lines:
        columns = [
            column.strip()
            for column in line.split("|")
        ]

        rows.append(columns)

    return rows


# ---------------------------------------------------------
# Validate table
# ---------------------------------------------------------
def validate_table(
    rows: list[list[str]],
) -> bool:
    """Validate table structure."""

    required_columns = [
        "Product",
        "Price",
        "Category",
        "Availability",
    ]

    headers = rows[0]

    for column in required_columns:
        if column not in headers:
            logger.error(
                "Missing required column: %s",
                column,
            )
            return False

    expected_columns = len(headers)

    for row in rows[1:]:
        if len(row) != expected_columns:
            logger.error(
                "Invalid row: %s",
                row,
            )
            return False

    return True


# ---------------------------------------------------------
# Normalize products
# ---------------------------------------------------------
def normalize_products(
    rows: list[list[str]],
) -> list[dict]:
    """Normalize extracted products."""

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

    return products


# ---------------------------------------------------------
# Create document summary
# ---------------------------------------------------------
def create_summary(
    products: list[dict],
) -> dict:
    """Create summary for one document."""

    total_products = len(products)

    total_value = sum(
        product["price"]
        for product in products
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

    average_price = (
        total_value / total_products
        if total_products
        else 0
    )

    return {
        "total_products": total_products,
        "total_value": total_value,
        "average_price": average_price,
        "available_products": available_products,
        "out_of_stock_products": out_of_stock_products,
    }


# ---------------------------------------------------------
# Process one document
# ---------------------------------------------------------
def process_document(
    file_path: Path,
) -> dict:
    """Process one document through the complete pipeline."""

    logger.info(
        "Starting processing: %s",
        file_path.name,
    )

    document = read_document(file_path)

    rows = extract_table(document)

    if not validate_table(rows):
        raise ValueError(
            f"Validation failed: {file_path.name}"
        )

    products = normalize_products(rows)

    summary = create_summary(products)

    result = {
        "document": file_path.name,
        "status": "SUCCESS",
        "products": products,
        "summary": summary,
    }

    logger.info(
        "Completed processing: %s",
        file_path.name,
    )

    return result


# ---------------------------------------------------------
# Create batch summary
# ---------------------------------------------------------
def create_batch_summary(
    results: list[dict],
) -> dict:
    """Create summary across all documents."""

    logger.info(
        "Creating batch summary"
    )

    total_documents = len(results)

    successful_documents = sum(
        1
        for result in results
        if result["status"] == "SUCCESS"
    )

    total_products = sum(
        result["summary"]["total_products"]
        for result in results
    )

    total_value = sum(
        result["summary"]["total_value"]
        for result in results
    )

    available_products = sum(
        result["summary"]["available_products"]
        for result in results
    )

    out_of_stock_products = sum(
        result["summary"]["out_of_stock_products"]
        for result in results
    )

    average_price = (
        total_value / total_products
        if total_products
        else 0
    )

    return {
        "total_documents": total_documents,
        "successful_documents": successful_documents,
        "total_products": total_products,
        "total_value": total_value,
        "average_product_price": average_price,
        "available_products": available_products,
        "out_of_stock_products": out_of_stock_products,
    }


# ---------------------------------------------------------
# Export batch result
# ---------------------------------------------------------
def export_batch_result(
    results: list[dict],
    batch_summary: dict,
) -> None:
    """Export complete batch result."""

    logger.info(
        "Exporting batch result to %s",
        OUTPUT_PATH.name,
    )

    output_data = {
        "pipeline": "GramSwaram Batch Document Processing",
        "documents": results,
        "batch_summary": batch_summary,
        "status": "SUCCESS",
    }

    with OUTPUT_PATH.open(
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
        "Batch result exported successfully"
    )


# ---------------------------------------------------------
# Display report
# ---------------------------------------------------------
def display_report(
    results: list[dict],
    batch_summary: dict,
) -> None:
    """Display batch processing report."""

    print("\n" + "=" * 70)
    print("GRAMSWARAM BATCH DOCUMENT PROCESSING")
    print("=" * 70)

    print("\nDOCUMENT RESULTS")
    print("-" * 70)

    for result in results:
        summary = result["summary"]

        print(
            f"\nDocument: {result['document']}"
        )

        print(
            f"Status: {result['status']}"
        )

        print(
            f"Products: {summary['total_products']}"
        )

        print(
            f"Total Value: "
            f"₹{summary['total_value']:.2f}"
        )

        print(
            f"Available: "
            f"{summary['available_products']}"
        )

        print(
            f"Out of Stock: "
            f"{summary['out_of_stock_products']}"
        )

    print("\nBATCH SUMMARY")
    print("-" * 70)

    print(
        f"Total Documents       : "
        f"{batch_summary['total_documents']}"
    )

    print(
        f"Successful Documents  : "
        f"{batch_summary['successful_documents']}"
    )

    print(
        f"Total Products        : "
        f"{batch_summary['total_products']}"
    )

    print(
        f"Total Product Value   : "
        f"₹{batch_summary['total_value']:.2f}"
    )

    print(
        f"Average Product Price : "
        f"₹{batch_summary['average_product_price']:.2f}"
    )

    print(
        f"Available Products    : "
        f"{batch_summary['available_products']}"
    )

    print(
        f"Out of Stock          : "
        f"{batch_summary['out_of_stock_products']}"
    )

    print("\n" + "=" * 70)
    print("Exercise 77 completed successfully.")
    print("=" * 70)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    logger.info(
        "Starting Exercise 77 - "
        "Batch Document Processing"
    )

    results = []

    for document_path in INPUT_DOCUMENTS:
        result = process_document(
            document_path
        )

        results.append(result)

    batch_summary = create_batch_summary(
        results
    )

    export_batch_result(
        results,
        batch_summary,
    )

    display_report(
        results,
        batch_summary,
    )

    logger.info(
        "Exercise 77 completed successfully"
    )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
if __name__ == "__main__":
    main()