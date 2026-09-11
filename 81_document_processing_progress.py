import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path


# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_progress_processing")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DOCUMENTS = [
    "77_product_catalog_1.txt",
    "77_product_catalog_2.txt",
    "78_invalid_catalog.txt",
]

MAX_WORKERS = 3


# ---------------------------------------------------------
# Parse Product Catalog
# ---------------------------------------------------------

def parse_product_catalog(file_path):
    """Read and parse a product catalog."""

    path = Path(file_path)

    logger.info(
        "Reading document: %s",
        file_path,
    )

    if not path.exists():
        raise FileNotFoundError(
            f"Document not found: {file_path}"
        )

    lines = path.read_text(
        encoding="utf-8"
    ).splitlines()

    table_lines = [
        line.strip()
        for line in lines
        if "|" in line
    ]

    if not table_lines:
        raise ValueError(
            "No table found in document"
        )

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
                "Invalid row: column count mismatch"
            )

        product = dict(
            zip(header, values)
        )

        products.append(product)

    if not products:
        raise ValueError(
            "No product records found"
        )

    return products


# ---------------------------------------------------------
# Process One Document
# ---------------------------------------------------------

def process_document(file_path):
    """Process one document in a worker thread."""

    file_name = Path(file_path).name

    logger.info(
        "Worker started: %s",
        file_name,
    )

    try:

        # Simulate processing time.
        time.sleep(2)

        products = parse_product_catalog(
            file_path
        )

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
            "Worker completed: %s",
            file_name,
        )

        return {
            "file": file_name,
            "status": "SUCCESS",
            "products": len(products),
            "total_value": total_value,
            "available": available_products,
            "out_of_stock": out_of_stock_products,
            "error": None,
        }

    except Exception as error:

        logger.error(
            "Worker failed: %s | %s",
            file_name,
            error,
        )

        return {
            "file": file_name,
            "status": "FAILED",
            "products": 0,
            "total_value": 0.0,
            "available": 0,
            "out_of_stock": 0,
            "error": str(error),
        }


# ---------------------------------------------------------
# Progress Display
# ---------------------------------------------------------

def display_progress(
    completed,
    total,
    successful,
    failed,
):
    """Display current batch progress."""

    percentage = (
        completed / total
    ) * 100

    print(
        f"Progress: {completed}/{total} "
        f"documents completed "
        f"({percentage:.1f}%) | "
        f"Success: {successful} | "
        f"Failed: {failed}"
    )


# ---------------------------------------------------------
# Parallel Processing with Progress Tracking
# ---------------------------------------------------------

def process_batch():

    logger.info(
        "Starting Exercise 81 - "
        "Document Processing with Progress Tracking"
    )

    total_documents = len(DOCUMENTS)

    logger.info(
        "Total documents: %d",
        total_documents,
    )

    logger.info(
        "Worker threads: %d",
        MAX_WORKERS,
    )

    results = []

    completed_documents = 0
    successful_documents = 0
    failed_documents = 0

    start_time = time.perf_counter()

    print()
    print("=" * 70)
    print("DOCUMENT PROCESSING PROGRESS")
    print("=" * 70)
    print()

    print(
        f"Starting batch: "
        f"0/{total_documents} documents completed"
    )

    # -----------------------------------------------------
    # Create Worker Pool
    # -----------------------------------------------------

    with ThreadPoolExecutor(
        max_workers=MAX_WORKERS
    ) as executor:

        future_to_document = {
            executor.submit(
                process_document,
                document,
            ): document
            for document in DOCUMENTS
        }

        # -------------------------------------------------
        # Process Completed Futures
        # -------------------------------------------------

        for future in as_completed(
            future_to_document
        ):

            document = future_to_document[
                future
            ]

            try:

                result = future.result()

                results.append(result)

                completed_documents += 1

                if result["status"] == "SUCCESS":

                    successful_documents += 1

                else:

                    failed_documents += 1

                logger.info(
                    "Progress update: %d/%d completed",
                    completed_documents,
                    total_documents,
                )

                display_progress(
                    completed_documents,
                    total_documents,
                    successful_documents,
                    failed_documents,
                )

            except Exception as error:

                completed_documents += 1
                failed_documents += 1

                logger.error(
                    "Unexpected error for %s: %s",
                    document,
                    error,
                )

                display_progress(
                    completed_documents,
                    total_documents,
                    successful_documents,
                    failed_documents,
                )

    end_time = time.perf_counter()

    processing_time = (
        end_time - start_time
    )

    return (
        results,
        processing_time,
        successful_documents,
        failed_documents,
    )


# ---------------------------------------------------------
# Final Report
# ---------------------------------------------------------

def display_final_report(
    results,
    processing_time,
    successful_documents,
    failed_documents,
):

    total_documents = len(results)

    total_products = sum(
        result["products"]
        for result in results
        if result["status"] == "SUCCESS"
    )

    total_value = sum(
        result["total_value"]
        for result in results
        if result["status"] == "SUCCESS"
    )

    total_available = sum(
        result["available"]
        for result in results
        if result["status"] == "SUCCESS"
    )

    total_out_of_stock = sum(
        result["out_of_stock"]
        for result in results
        if result["status"] == "SUCCESS"
    )

    print()
    print("=" * 70)
    print("FINAL DOCUMENT PROCESSING REPORT")
    print("=" * 70)

    print()
    print("SUCCESSFUL DOCUMENTS")

    for result in results:

        if result["status"] == "SUCCESS":

            print(
                f"{result['file']} | "
                f"Products: {result['products']} | "
                f"Value: ₹{result['total_value']:.2f}"
            )

    print()
    print("FAILED DOCUMENTS")

    for result in results:

        if result["status"] == "FAILED":

            print(
                f"{result['file']} | "
                f"Error: {result['error']}"
            )

    print()
    print("BATCH SUMMARY")
    print("-" * 70)

    print(
        f"Total Documents       : "
        f"{total_documents}"
    )

    print(
        f"Successful Documents  : "
        f"{successful_documents}"
    )

    print(
        f"Failed Documents      : "
        f"{failed_documents}"
    )

    print(
        f"Completed Documents   : "
        f"{successful_documents + failed_documents}"
    )

    print(
        f"Total Products        : "
        f"{total_products}"
    )

    print(
        f"Total Product Value   : "
        f"₹{total_value:.2f}"
    )

    print(
        f"Available Products    : "
        f"{total_available}"
    )

    print(
        f"Out of Stock          : "
        f"{total_out_of_stock}"
    )

    print(
        f"Processing Time       : "
        f"{processing_time:.2f} seconds"
    )

    print()
    print(
        "Exercise 81 completed successfully."
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    (
        results,
        processing_time,
        successful_documents,
        failed_documents,
    ) = process_batch()

    display_final_report(
        results,
        processing_time,
        successful_documents,
        failed_documents,
    )

    logger.info(
        "Exercise 81 completed successfully"
    )


if __name__ == "__main__":
    main()