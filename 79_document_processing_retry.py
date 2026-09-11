import logging
import time
from pathlib import Path


# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_document_retry")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

MAX_RETRIES = 2
RETRY_DELAY_SECONDS = 1

DOCUMENTS = [
    "77_product_catalog_1.txt",
    "77_product_catalog_2.txt",
    "78_invalid_catalog.txt",
]


# ---------------------------------------------------------
# Simulated Transient Failures
# ---------------------------------------------------------
# This is only for learning retry logic.
#
# First document:
#   Fails twice temporarily
#   Succeeds on attempt 3
#
# Second document:
#   Fails more times than allowed retries
#   Therefore it finally fails
#
# Third document:
#   Has a permanent validation error
# ---------------------------------------------------------

SIMULATED_TRANSIENT_FAILURES = {
    "77_product_catalog_1.txt": 2,
    "77_product_catalog_2.txt": 5,
}


# ---------------------------------------------------------
# Custom Exception
# ---------------------------------------------------------

class TransientProcessingError(Exception):
    """Represents a temporary processing failure."""


# ---------------------------------------------------------
# Parse Product Catalog
# ---------------------------------------------------------

def parse_product_catalog(file_path):
    """Read and parse a product catalog."""

    logger.info("Reading document: %s", file_path)

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"Document not found: {file_path}")

    lines = path.read_text(encoding="utf-8").splitlines()

    table_lines = [
        line.strip()
        for line in lines
        if "|" in line
    ]

    if not table_lines:
        raise ValueError("No table found in document")

    header = [
        column.strip()
        for column in table_lines[0].split("|")
    ]

    required_columns = [
        "Product",
        "Price",
        "Category",
        "Availability",
    ]

    for column in required_columns:
        if column not in header:
            raise ValueError(
                f"Missing required column: {column}"
            )

    products = []

    for line in table_lines[1:]:
        values = [
            value.strip()
            for value in line.split("|")
        ]

        if len(values) != len(header):
            raise ValueError(
                "Invalid row: number of columns does not match header"
            )

        product = dict(zip(header, values))
        products.append(product)

    if not products:
        raise ValueError("No product records found")

    return products


# ---------------------------------------------------------
# Simulate Temporary Failure
# ---------------------------------------------------------

def simulate_transient_failure(file_name, attempt):
    """
    Simulate temporary failures for learning purposes.
    """

    failure_limit = SIMULATED_TRANSIENT_FAILURES.get(
        file_name,
        0,
    )

    if attempt <= failure_limit:
        raise TransientProcessingError(
            f"Simulated temporary failure on attempt {attempt}"
        )


# ---------------------------------------------------------
# Process One Document
# ---------------------------------------------------------

def process_document_with_retry(file_path):
    """
    Process one document with retry logic.

    MAX_RETRIES = 2 means:
        Attempt 1
        Attempt 2
        Attempt 3

    So total possible attempts = 3.
    """

    file_name = Path(file_path).name
    total_attempts = MAX_RETRIES + 1

    for attempt in range(1, total_attempts + 1):

        logger.info(
            "Processing %s | Attempt %d/%d",
            file_name,
            attempt,
            total_attempts,
        )

        try:
            # Simulate a temporary failure.
            simulate_transient_failure(
                file_name,
                attempt,
            )

            # Actual document processing.
            products = parse_product_catalog(file_path)

            total_value = 0.0
            available_products = 0
            out_of_stock_products = 0

            for product in products:

                price_text = (
                    product["Price"]
                    .replace("₹", "")
                    .replace(",", "")
                    .strip()
                )

                price = float(price_text)

                total_value += price

                availability = (
                    product["Availability"]
                    .strip()
                    .lower()
                )

                if availability == "available":
                    available_products += 1

                elif availability == "out of stock":
                    out_of_stock_products += 1

            logger.info(
                "SUCCESS: %s processed on attempt %d",
                file_name,
                attempt,
            )

            return {
                "file": file_name,
                "status": "SUCCESS",
                "attempts": attempt,
                "products": len(products),
                "total_value": total_value,
                "available": available_products,
                "out_of_stock": out_of_stock_products,
            }

        except TransientProcessingError as error:

            logger.warning(
                "Temporary failure: %s | Attempt %d/%d",
                error,
                attempt,
                total_attempts,
            )

            if attempt < total_attempts:

                logger.info(
                    "Retrying %s after %d second(s)...",
                    file_name,
                    RETRY_DELAY_SECONDS,
                )

                time.sleep(RETRY_DELAY_SECONDS)

            else:

                logger.error(
                    "FINAL FAILURE: %s exhausted all retry attempts",
                    file_name,
                )

                return {
                    "file": file_name,
                    "status": "FAILED",
                    "attempts": attempt,
                    "products": 0,
                    "total_value": 0.0,
                    "available": 0,
                    "out_of_stock": 0,
                    "error": str(error),
                }

        except (ValueError, FileNotFoundError) as error:

            # These are permanent errors.
            # Retrying them would not solve the problem.

            logger.error(
                "Permanent processing error in %s: %s",
                file_name,
                error,
            )

            return {
                "file": file_name,
                "status": "FAILED",
                "attempts": attempt,
                "products": 0,
                "total_value": 0.0,
                "available": 0,
                "out_of_stock": 0,
                "error": str(error),
            }


# ---------------------------------------------------------
# Batch Processing
# ---------------------------------------------------------

def main():

    logger.info(
        "Starting Exercise 79 - Document Processing with Retry Logic"
    )

    results = []

    for document in DOCUMENTS:

        logger.info(
            "Starting document: %s",
            document,
        )

        result = process_document_with_retry(document)

        results.append(result)

    # -----------------------------------------------------
    # Calculate Batch Statistics
    # -----------------------------------------------------

    successful_documents = [
        result
        for result in results
        if result["status"] == "SUCCESS"
    ]

    failed_documents = [
        result
        for result in results
        if result["status"] == "FAILED"
    ]

    total_attempts = sum(
        result["attempts"]
        for result in results
    )

    total_retries = sum(
        max(result["attempts"] - 1, 0)
        for result in results
    )

    total_products = sum(
        result["products"]
        for result in successful_documents
    )

    total_value = sum(
        result["total_value"]
        for result in successful_documents
    )

    total_available = sum(
        result["available"]
        for result in successful_documents
    )

    total_out_of_stock = sum(
        result["out_of_stock"]
        for result in successful_documents
    )

    # -----------------------------------------------------
    # Display Results
    # -----------------------------------------------------

    print()
    print("=" * 65)
    print("DOCUMENT PROCESSING WITH RETRY RESULTS")
    print("=" * 65)

    print()
    print("SUCCESSFUL DOCUMENTS")

    for result in successful_documents:

        print(
            f"{result['file']} | "
            f"Attempts: {result['attempts']} | "
            f"Products: {result['products']} | "
            f"Value: ₹{result['total_value']:.2f}"
        )

    print()
    print("FAILED DOCUMENTS")

    for result in failed_documents:

        print(
            f"{result['file']} | "
            f"Attempts: {result['attempts']} | "
            f"Error: {result['error']}"
        )

    print()
    print("RETRY STATISTICS")
    print("-" * 65)

    print(f"Total Documents       : {len(results)}")
    print(f"Successful Documents  : {len(successful_documents)}")
    print(f"Failed Documents      : {len(failed_documents)}")
    print(f"Total Processing Attempts : {total_attempts}")
    print(f"Total Retries         : {total_retries}")

    print()
    print("SUCCESSFUL DATA SUMMARY")
    print("-" * 65)

    print(f"Total Products        : {total_products}")
    print(f"Total Product Value   : ₹{total_value:.2f}")
    print(f"Available Products    : {total_available}")
    print(f"Out of Stock          : {total_out_of_stock}")

    print()
    print("Exercise 79 completed successfully.")

    logger.info(
        "Exercise 79 completed successfully"
    )


# ---------------------------------------------------------
# Program Entry Point
# ---------------------------------------------------------

if __name__ == "__main__":
    main()