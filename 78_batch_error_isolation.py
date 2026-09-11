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

logger = logging.getLogger("gram_swaram_batch_error_isolation")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

INPUT_DOCUMENTS = [
    BASE_DIR / "77_product_catalog_1.txt",
    BASE_DIR / "78_invalid_catalog.txt",
    BASE_DIR / "77_product_catalog_2.txt",
]

OUTPUT_PATH = BASE_DIR / "78_error_isolation_output.json"


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
        "Loaded %d characters from %s",
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

    return [
        [
            column.strip()
            for column in line.split("|")
        ]
        for line in lines
    ]


# ---------------------------------------------------------
# Validate table
# ---------------------------------------------------------
def validate_table(
    rows: list[list[str]],
) -> None:
    """Validate table and raise an error if invalid."""

    required_columns = [
        "Product",
        "Price",
        "Category",
        "Availability",
    ]

    headers = rows[0]

    logger.info(
        "Validating required columns"
    )

    for column in required_columns:
        if column not in headers:
            raise ValueError(
                f"Missing required column: {column}"
            )

    expected_columns = len(headers)

    for row_number, row in enumerate(
        rows[1:],
        start=2,
    ):
        if len(row) != expected_columns:
            raise ValueError(
                f"Invalid row {row_number}: "
                f"expected {expected_columns} columns, "
                f"found {len(row)}"
            )

    logger.info(
        "Validation successful"
    )


# ---------------------------------------------------------
# Normalize products
# ---------------------------------------------------------
def normalize_products(
    rows: list[list[str]],
) -> list[dict]:
    """Normalize product data."""

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
        "Normalized %d products",
        len(products),
    )

    return products


# ---------------------------------------------------------
# Create summary
# ---------------------------------------------------------
def create_summary(
    products: list[dict],
) -> dict:
    """Create document summary."""

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

    return {
        "total_products": total_products,
        "total_value": total_value,
        "average_price": (
            total_value / total_products
            if total_products
            else 0
        ),
        "available_products": available_products,
        "out_of_stock_products": out_of_stock_products,
    }


# ---------------------------------------------------------
# Process one document
# ---------------------------------------------------------
def process_document(
    file_path: Path,
) -> dict:
    """Process one document."""

    logger.info(
        "Starting processing: %s",
        file_path.name,
    )

    document = read_document(file_path)

    rows = extract_table(document)

    validate_table(rows)

    products = normalize_products(rows)

    summary = create_summary(products)

    logger.info(
        "Successfully processed: %s",
        file_path.name,
    )

    return {
        "document": file_path.name,
        "status": "SUCCESS",
        "products": products,
        "summary": summary,
    }


# ---------------------------------------------------------
# Process batch with error isolation
# ---------------------------------------------------------
def process_batch() -> tuple[list[dict], list[dict]]:
    """Process all documents without stopping on errors."""

    logger.info(
        "Starting batch processing with error isolation"
    )

    successful_results = []
    failed_results = []

    for document_path in INPUT_DOCUMENTS:

        try:

            result = process_document(
                document_path
            )

            successful_results.append(result)

        except Exception as error:

            logger.exception(
                "Failed to process %s",
                document_path.name,
            )

            failed_results.append(
                {
                    "document": document_path.name,
                    "status": "FAILED",
                    "error": str(error),
                }
            )

            logger.warning(
                "Continuing batch processing after failure: %s",
                document_path.name,
            )

    return successful_results, failed_results


# ---------------------------------------------------------
# Create batch summary
# ---------------------------------------------------------
def create_batch_summary(
    successful_results: list[dict],
    failed_results: list[dict],
) -> dict:
    """Create batch summary."""

    total_documents = (
        len(successful_results)
        + len(failed_results)
    )

    total_products = sum(
        result["summary"]["total_products"]
        for result in successful_results
    )

    total_value = sum(
        result["summary"]["total_value"]
        for result in successful_results
    )

    available_products = sum(
        result["summary"]["available_products"]
        for result in successful_results
    )

    out_of_stock_products = sum(
        result["summary"]["out_of_stock_products"]
        for result in successful_results
    )

    return {
        "total_documents": total_documents,
        "successful_documents": len(
            successful_results
        ),
        "failed_documents": len(
            failed_results
        ),
        "total_products_from_successful_documents": (
            total_products
        ),
        "total_value_from_successful_documents": (
            total_value
        ),
        "available_products": available_products,
        "out_of_stock_products": out_of_stock_products,
    }


# ---------------------------------------------------------
# Export result
# ---------------------------------------------------------
def export_result(
    successful_results: list[dict],
    failed_results: list[dict],
    batch_summary: dict,
) -> None:
    """Export successful and failed results."""

    logger.info(
        "Exporting error-isolation report"
    )

    output_data = {
        "pipeline": (
            "GramSwaram Batch Processing "
            "with Error Isolation"
        ),
        "successful_documents": successful_results,
        "failed_documents": failed_results,
        "batch_summary": batch_summary,
        "status": "COMPLETED_WITH_ISOLATION",
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
        "Error-isolation report exported successfully"
    )


# ---------------------------------------------------------
# Display report
# ---------------------------------------------------------
def display_report(
    successful_results: list[dict],
    failed_results: list[dict],
    batch_summary: dict,
) -> None:
    """Display final batch report."""

    print("\n" + "=" * 70)
    print("GRAMSWARAM BATCH ERROR ISOLATION")
    print("=" * 70)

    print("\nSUCCESSFUL DOCUMENTS")
    print("-" * 70)

    for result in successful_results:

        summary = result["summary"]

        print(
            f"{result['document']} | "
            f"Products: {summary['total_products']} | "
            f"Value: ₹{summary['total_value']:.2f}"
        )

    print("\nFAILED DOCUMENTS")
    print("-" * 70)

    for result in failed_results:

        print(
            f"{result['document']} | "
            f"Status: {result['status']}"
        )

        print(
            f"Error: {result['error']}"
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
        f"Failed Documents      : "
        f"{batch_summary['failed_documents']}"
    )

    print(
        f"Total Products        : "
        f"{batch_summary['total_products_from_successful_documents']}"
    )

    print(
        f"Total Product Value   : "
        f"₹{batch_summary['total_value_from_successful_documents']:.2f}"
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
    print(
        "Exercise 78 completed successfully."
    )
    print("=" * 70)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    logger.info(
        "Starting Exercise 78 - "
        "Batch Processing with Error Isolation"
    )

    successful_results, failed_results = (
        process_batch()
    )

    batch_summary = create_batch_summary(
        successful_results,
        failed_results,
    )

    export_result(
        successful_results,
        failed_results,
        batch_summary,
    )

    display_report(
        successful_results,
        failed_results,
        batch_summary,
    )

    logger.info(
        "Exercise 78 completed successfully"
    )


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------
if __name__ == "__main__":
    main()