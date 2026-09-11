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

logger = logging.getLogger("gram_swaram_parallel_processing")


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
    """
    Process one document.

    This function is executed by a worker thread.
    """

    file_name = Path(file_path).name

    logger.info(
        "Worker started processing: %s",
        file_name,
    )

    try:

        # Simulate a small processing delay.
        # This makes parallel execution easier to observe.
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
            "Worker successfully processed: %s",
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
            "Worker failed processing %s: %s",
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
# Parallel Batch Processing
# ---------------------------------------------------------

def process_documents_in_parallel():

    logger.info(
        "Starting Exercise 80 - Parallel Document Processing"
    )

    logger.info(
        "Documents to process: %d",
        len(DOCUMENTS),
    )

    logger.info(
        "Maximum worker threads: %d",
        MAX_WORKERS,
    )

    results = []

    start_time = time.perf_counter()

    # -----------------------------------------------------
    # Thread Pool
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

        for future in as_completed(
            future_to_document
        ):

            document = future_to_document[
                future
            ]

            try:

                result = future.result()

                results.append(result)

                logger.info(
                    "Completed future for: %s",
                    document,
                )

            except Exception as error:

                logger.error(
                    "Unexpected worker error for %s: %s",
                    document,
                    error,
                )

    end_time = time.perf_counter()

    processing_time = (
        end_time - start_time
    )

    return results, processing_time


# ---------------------------------------------------------
# Display Results
# ---------------------------------------------------------

def display_results(
    results,
    processing_time,
):

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

    print()
    print("=" * 70)
    print("PARALLEL DOCUMENT PROCESSING RESULTS")
    print("=" * 70)

    print()
    print("SUCCESSFUL DOCUMENTS")

    for result in successful_documents:

        print(
            f"{result['file']} | "
            f"Products: {result['products']} | "
            f"Value: ₹{result['total_value']:.2f}"
        )

    print()
    print("FAILED DOCUMENTS")

    for result in failed_documents:

        print(
            f"{result['file']} | "
            f"Error: {result['error']}"
        )

    print()
    print("BATCH SUMMARY")
    print("-" * 70)

    print(
        f"Total Documents       : {len(results)}"
    )

    print(
        f"Successful Documents  : "
        f"{len(successful_documents)}"
    )

    print(
        f"Failed Documents      : "
        f"{len(failed_documents)}"
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
        "Exercise 80 completed successfully."
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    results, processing_time = (
        process_documents_in_parallel()
    )

    display_results(
        results,
        processing_time,
    )

    logger.info(
        "Exercise 80 completed successfully"
    )


if __name__ == "__main__":
    main()