import hashlib
import json
import logging
from pathlib import Path
from typing import Dict, List


# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_change_detection")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DOCUMENTS = [
    "77_product_catalog_1.txt",
    "77_product_catalog_2.txt",
]

STATE_FILE = Path("84_document_hashes.json")

REQUIRED_COLUMNS = [
    "Product",
    "Price",
    "Category",
    "Availability",
]


# ---------------------------------------------------------
# Hash Calculation
# ---------------------------------------------------------

def calculate_document_hash(file_path: str) -> str:
    """
    Calculate the SHA-256 hash of a document.
    """

    logger.info("Calculating hash: %s", file_path)

    file_content = Path(file_path).read_bytes()

    document_hash = hashlib.sha256(file_content).hexdigest()

    logger.info(
        "Hash calculated: %s | Hash: %s",
        file_path,
        document_hash[:12],
    )

    return document_hash


# ---------------------------------------------------------
# Load Previous Hash State
# ---------------------------------------------------------

def load_previous_state() -> Dict[str, str]:
    """
    Load previously stored document hashes.
    """

    if not STATE_FILE.exists():

        logger.info(
            "No previous hash state found. "
            "Starting with an empty state."
        )

        return {}

    try:

        state = json.loads(
            STATE_FILE.read_text(encoding="utf-8")
        )

        logger.info(
            "Previous hash state loaded successfully. "
            "Tracked documents: %d",
            len(state),
        )

        return state

    except json.JSONDecodeError as error:

        logger.error(
            "Invalid hash state file: %s",
            error,
        )

        return {}


# ---------------------------------------------------------
# Save Hash State
# ---------------------------------------------------------

def save_state(state: Dict[str, str]) -> None:
    """
    Save current document hashes.
    """

    STATE_FILE.write_text(
        json.dumps(
            state,
            indent=4,
        ),
        encoding="utf-8",
    )

    logger.info(
        "Hash state saved. Tracked documents: %d",
        len(state),
    )


# ---------------------------------------------------------
# Product Catalog Parser
# ---------------------------------------------------------

def parse_product_catalog(file_path: str) -> Dict:
    """
    Parse a product catalog and calculate statistics.
    """

    logger.info(
        "Processing changed/new document: %s",
        file_path,
    )

    lines = Path(file_path).read_text(
        encoding="utf-8"
    ).splitlines()

    table_lines = [
        line.strip()
        for line in lines
        if "|" in line
    ]

    if len(table_lines) < 2:
        raise ValueError(
            "Product table is missing."
        )

    headers = [
        header.strip()
        for header in table_lines[0].split("|")
    ]

    for required_column in REQUIRED_COLUMNS:

        if required_column not in headers:

            raise ValueError(
                f"Missing required column: "
                f"{required_column}"
            )

    products = []

    for line in table_lines[1:]:

        values = [
            value.strip()
            for value in line.split("|")
        ]

        if len(values) != len(headers):
            continue

        row = dict(
            zip(headers, values)
        )

        price_text = (
            row["Price"]
            .replace("₹", "")
            .replace(",", "")
            .strip()
        )

        price = float(price_text)

        products.append(
            {
                "product": row["Product"],
                "price": price,
                "category": row["Category"],
                "availability": row["Availability"],
            }
        )

    total_value = sum(
        product["price"]
        for product in products
    )

    available_products = sum(
        1
        for product in products
        if product["availability"].lower()
        == "available"
    )

    out_of_stock = sum(
        1
        for product in products
        if product["availability"].lower()
        == "out of stock"
    )

    return {
        "file": file_path,
        "products": len(products),
        "total_value": total_value,
        "available": available_products,
        "out_of_stock": out_of_stock,
    }


# ---------------------------------------------------------
# Change Detection
# ---------------------------------------------------------

def detect_and_process_documents(
    documents: List[str],
) -> Dict:

    logger.info(
        "Starting document change detection "
        "for %d documents",
        len(documents),
    )

    previous_state = load_previous_state()

    current_state = dict(previous_state)

    new_documents = []
    unchanged_documents = []
    changed_documents = []
    failed_documents = []
    processed_results = []

    for document in documents:

        logger.info(
            "Checking document: %s",
            document,
        )

        try:

            current_hash = calculate_document_hash(
                document
            )

            previous_hash = previous_state.get(
                document
            )

            # -------------------------------------------------
            # New Document
            # -------------------------------------------------

            if previous_hash is None:

                logger.info(
                    "NEW document detected: %s",
                    document,
                )

                result = parse_product_catalog(
                    document
                )

                processed_results.append(result)

                new_documents.append(document)

                current_state[document] = current_hash

                continue

            # -------------------------------------------------
            # Unchanged Document
            # -------------------------------------------------

            if previous_hash == current_hash:

                logger.info(
                    "UNCHANGED document detected. "
                    "Skipping: %s",
                    document,
                )

                unchanged_documents.append(
                    document
                )

                continue

            # -------------------------------------------------
            # Changed Document
            # -------------------------------------------------

            logger.warning(
                "CHANGED document detected: %s",
                document,
            )

            logger.info(
                "Previous hash: %s",
                previous_hash[:12],
            )

            logger.info(
                "Current hash: %s",
                current_hash[:12],
            )

            result = parse_product_catalog(
                document
            )

            processed_results.append(result)

            changed_documents.append(document)

            current_state[document] = current_hash

        except Exception as error:

            logger.error(
                "Failed to process %s: %s",
                document,
                error,
            )

            failed_documents.append(
                {
                    "file": document,
                    "error": str(error),
                }
            )

    save_state(current_state)

    return {
        "new": new_documents,
        "unchanged": unchanged_documents,
        "changed": changed_documents,
        "failed": failed_documents,
        "results": processed_results,
    }


# ---------------------------------------------------------
# Report
# ---------------------------------------------------------

def display_report(report: Dict) -> None:

    new_documents = report["new"]
    unchanged_documents = report["unchanged"]
    changed_documents = report["changed"]
    failed_documents = report["failed"]
    results = report["results"]

    total_products = sum(
        result["products"]
        for result in results
    )

    total_value = sum(
        result["total_value"]
        for result in results
    )

    total_available = sum(
        result["available"]
        for result in results
    )

    total_out_of_stock = sum(
        result["out_of_stock"]
        for result in results
    )

    print()
    print("=" * 70)
    print("DOCUMENT PROCESSING WITH CHANGE DETECTION")
    print("=" * 70)

    print()
    print("NEW DOCUMENTS")
    print("-" * 70)

    if new_documents:

        for document in new_documents:
            print(
                f"{document} | New - Processed"
            )

    else:
        print("No new documents.")

    print()
    print("UNCHANGED DOCUMENTS")
    print("-" * 70)

    if unchanged_documents:

        for document in unchanged_documents:
            print(
                f"{document} | "
                f"Unchanged - Skipped"
            )

    else:
        print("No unchanged documents.")

    print()
    print("CHANGED DOCUMENTS")
    print("-" * 70)

    if changed_documents:

        for document in changed_documents:
            print(
                f"{document} | "
                f"Changed - Reprocessed"
            )

    else:
        print("No changed documents.")

    print()
    print("FAILED DOCUMENTS")
    print("-" * 70)

    if failed_documents:

        for item in failed_documents:

            print(
                f"{item['file']} | "
                f"Error: {item['error']}"
            )

    else:

        print("No failed documents.")

    print()
    print("CHANGE DETECTION SUMMARY")
    print("-" * 70)

    print(
        f"Documents Checked     : "
        f"{len(DOCUMENTS)}"
    )

    print(
        f"New Documents         : "
        f"{len(new_documents)}"
    )

    print(
        f"Unchanged Documents   : "
        f"{len(unchanged_documents)}"
    )

    print(
        f"Changed Documents     : "
        f"{len(changed_documents)}"
    )

    print(
        f"Failed Documents      : "
        f"{len(failed_documents)}"
    )

    print()
    print("PROCESSED DATA SUMMARY")
    print("-" * 70)

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

    print()
    print("Exercise 84 completed successfully.")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    logger.info(
        "Starting Exercise 84 - "
        "Document Processing with Change Detection"
    )

    report = detect_and_process_documents(
        DOCUMENTS
    )

    display_report(report)

    logger.info(
        "Exercise 84 completed successfully"
    )


if __name__ == "__main__":
    main()