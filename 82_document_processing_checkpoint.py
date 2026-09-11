import json
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

logger = logging.getLogger(
    "gram_swaram_checkpoint_processing"
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DOCUMENTS = [
    "77_product_catalog_1.txt",
    "77_product_catalog_2.txt",
    "78_invalid_catalog.txt",
]

CHECKPOINT_FILE = Path(
    "82_processing_checkpoint.json"
)


# ---------------------------------------------------------
# Load Checkpoint
# ---------------------------------------------------------

def load_checkpoint():
    """Load previously completed documents."""

    if not CHECKPOINT_FILE.exists():

        logger.info(
            "No checkpoint found. Starting fresh."
        )

        return {
            "completed_documents": [],
            "results": [],
        }

    try:

        data = json.loads(
            CHECKPOINT_FILE.read_text(
                encoding="utf-8"
            )
        )

        logger.info(
            "Checkpoint loaded successfully."
        )

        logger.info(
            "Previously completed documents: %d",
            len(data.get("completed_documents", [])),
        )

        return data

    except json.JSONDecodeError as error:

        logger.error(
            "Checkpoint file is invalid: %s",
            error,
        )

        logger.info(
            "Starting with an empty checkpoint."
        )

        return {
            "completed_documents": [],
            "results": [],
        }


# ---------------------------------------------------------
# Save Checkpoint
# ---------------------------------------------------------

def save_checkpoint(
    completed_documents,
    results,
):
    """Save current processing state."""

    checkpoint = {
        "completed_documents": completed_documents,
        "results": results,
    }

    CHECKPOINT_FILE.write_text(
        json.dumps(
            checkpoint,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    logger.info(
        "Checkpoint saved. Completed: %d",
        len(completed_documents),
    )


# ---------------------------------------------------------
# Parse Product Catalog
# ---------------------------------------------------------

def parse_product_catalog(file_path):

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

        products.append(
            dict(zip(header, values))
        )

    if not products:

        raise ValueError(
            "No product records found"
        )

    return products


# ---------------------------------------------------------
# Process Document
# ---------------------------------------------------------

def process_document(file_path):

    file_name = Path(file_path).name

    logger.info(
        "Starting document processing: %s",
        file_name,
    )

    try:

        # Simulate document processing time.
        time.sleep(1)

        products = parse_product_catalog(
            file_path
        )

        total_value = 0.0
        available = 0
        out_of_stock = 0

        for product in products:

            price = float(
                product["Price"]
                .replace("₹", "")
                .replace(",", "")
                .strip()
            )

            total_value += price

            availability = (
                product["Availability"]
                .strip()
                .lower()
            )

            if availability == "available":

                available += 1

            elif availability == "out of stock":

                out_of_stock += 1

        logger.info(
            "Successfully processed: %s",
            file_name,
        )

        return {
            "file": file_name,
            "status": "SUCCESS",
            "products": len(products),
            "total_value": total_value,
            "available": available,
            "out_of_stock": out_of_stock,
            "error": None,
        }

    except Exception as error:

        logger.error(
            "Failed to process %s: %s",
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
# Process Batch with Checkpointing
# ---------------------------------------------------------

def process_batch():

    logger.info(
        "Starting Exercise 82 - "
        "Document Processing with Checkpointing"
    )

    checkpoint = load_checkpoint()

    completed_documents = checkpoint[
        "completed_documents"
    ]

    results = checkpoint["results"]

    logger.info(
        "Documents in current batch: %d",
        len(DOCUMENTS),
    )

    for document in DOCUMENTS:

        file_name = Path(document).name

        # -------------------------------------------------
        # Check Whether Already Completed
        # -------------------------------------------------

        if file_name in completed_documents:

            logger.info(
                "Skipping already completed document: %s",
                file_name,
            )

            continue

        # -------------------------------------------------
        # Process Document
        # -------------------------------------------------

        result = process_document(
            document
        )

        results.append(result)

        # -------------------------------------------------
        # Save Successful Documents
        # -------------------------------------------------

        if result["status"] == "SUCCESS":

            completed_documents.append(
                file_name
            )

            save_checkpoint(
                completed_documents,
                results,
            )

        else:

            logger.warning(
                "Document failed and will not "
                "be marked as completed: %s",
                file_name,
            )

            # Save the current results even if
            # the document failed.
            save_checkpoint(
                completed_documents,
                results,
            )


# ---------------------------------------------------------
# Final Report
# ---------------------------------------------------------

def display_report():

    checkpoint = load_checkpoint()

    results = checkpoint["results"]

    successful = [
        result
        for result in results
        if result["status"] == "SUCCESS"
    ]

    failed = [
        result
        for result in results
        if result["status"] == "FAILED"
    ]

    total_products = sum(
        result["products"]
        for result in successful
    )

    total_value = sum(
        result["total_value"]
        for result in successful
    )

    total_available = sum(
        result["available"]
        for result in successful
    )

    total_out_of_stock = sum(
        result["out_of_stock"]
        for result in successful
    )

    print()
    print("=" * 70)
    print("CHECKPOINTED DOCUMENT PROCESSING")
    print("=" * 70)

    print()
    print("SUCCESSFUL DOCUMENTS")

    for result in successful:

        print(
            f"{result['file']} | "
            f"Products: {result['products']} | "
            f"Value: ₹{result['total_value']:.2f}"
        )

    print()
    print("FAILED DOCUMENTS")

    for result in failed:

        print(
            f"{result['file']} | "
            f"Error: {result['error']}"
        )

    print()
    print("CHECKPOINT SUMMARY")
    print("-" * 70)

    print(
        f"Completed Documents : "
        f"{len(checkpoint['completed_documents'])}"
    )

    print(
        f"Failed Documents    : "
        f"{len(failed)}"
    )

    print()
    print("DATA SUMMARY")
    print("-" * 70)

    print(
        f"Total Products      : "
        f"{total_products}"
    )

    print(
        f"Total Product Value : "
        f"₹{total_value:.2f}"
    )

    print(
        f"Available Products  : "
        f"{total_available}"
    )

    print(
        f"Out of Stock        : "
        f"{total_out_of_stock}"
    )

    print()
    print(
        "Exercise 82 completed successfully."
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    process_batch()

    display_report()

    logger.info(
        "Exercise 82 completed successfully"
    )


if __name__ == "__main__":
    main()