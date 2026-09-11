import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_versioning")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DOCUMENTS = [
    "77_product_catalog_1.txt",
    "77_product_catalog_2.txt",
]

VERSION_FILE = Path("85_document_versions.json")

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
    """Calculate SHA-256 hash of a document."""

    logger.info("Calculating hash: %s", file_path)

    content = Path(file_path).read_bytes()

    document_hash = hashlib.sha256(content).hexdigest()

    logger.info(
        "Hash calculated: %s | Hash: %s",
        file_path,
        document_hash[:12],
    )

    return document_hash


# ---------------------------------------------------------
# Load Version History
# ---------------------------------------------------------

def load_version_history() -> Dict:
    """Load previously stored document version history."""

    if not VERSION_FILE.exists():

        logger.info(
            "No version history found. Starting fresh."
        )

        return {}

    try:

        history = json.loads(
            VERSION_FILE.read_text(
                encoding="utf-8"
            )
        )

        logger.info(
            "Version history loaded successfully. "
            "Documents tracked: %d",
            len(history),
        )

        return history

    except json.JSONDecodeError as error:

        logger.error(
            "Invalid version history file: %s",
            error,
        )

        return {}


# ---------------------------------------------------------
# Save Version History
# ---------------------------------------------------------

def save_version_history(history: Dict) -> None:
    """Save document version history."""

    VERSION_FILE.write_text(
        json.dumps(
            history,
            indent=4,
        ),
        encoding="utf-8",
    )

    logger.info(
        "Version history saved successfully."
    )


# ---------------------------------------------------------
# Product Catalog Parser
# ---------------------------------------------------------

def parse_product_catalog(file_path: str) -> Dict:
    """Parse product catalog and calculate statistics."""

    logger.info(
        "Processing document: %s",
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
        "products": len(products),
        "total_value": total_value,
        "available": available_products,
        "out_of_stock": out_of_stock,
    }


# ---------------------------------------------------------
# Process One Document
# ---------------------------------------------------------

def process_document(
    document: str,
    history: Dict,
) -> Dict:

    logger.info(
        "Checking document: %s",
        document,
    )

    current_hash = calculate_document_hash(
        document
    )

    previous_versions = history.get(
        document,
        []
    )

    # -----------------------------------------------------
    # Check whether this exact version already exists
    # -----------------------------------------------------

    existing_version = next(
        (
            version
            for version in previous_versions
            if version["hash"] == current_hash
        ),
        None,
    )

    if existing_version:

        logger.info(
            "Existing version detected: %s | Version %d",
            document,
            existing_version["version"],
        )

        return {
            "status": "unchanged",
            "document": document,
            "version": existing_version["version"],
            "data": existing_version["data"],
        }

    # -----------------------------------------------------
    # New Version
    # -----------------------------------------------------

    new_version_number = (
        len(previous_versions) + 1
    )

    logger.info(
        "New version detected: %s | Version %d",
        document,
        new_version_number,
    )

    data = parse_product_catalog(document)

    version_record = {
        "version": new_version_number,
        "hash": current_hash,
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "data": data,
    }

    history.setdefault(
        document,
        []
    ).append(version_record)

    logger.info(
        "Version %d saved for %s",
        new_version_number,
        document,
    )

    return {
        "status": "new_version",
        "document": document,
        "version": new_version_number,
        "data": data,
    }


# ---------------------------------------------------------
# Process All Documents
# ---------------------------------------------------------

def process_documents(
    documents: List[str],
) -> Dict:

    history = load_version_history()

    results = []

    for document in documents:

        try:

            result = process_document(
                document,
                history,
            )

            results.append(result)

        except Exception as error:

            logger.error(
                "Failed to process %s: %s",
                document,
                error,
            )

            results.append(
                {
                    "status": "failed",
                    "document": document,
                    "error": str(error),
                }
            )

    save_version_history(history)

    return {
        "history": history,
        "results": results,
    }


# ---------------------------------------------------------
# Display Report
# ---------------------------------------------------------

def display_report(report: Dict) -> None:

    history = report["history"]
    results = report["results"]

    print()
    print("=" * 70)
    print("DOCUMENT PROCESSING WITH VERSIONING")
    print("=" * 70)

    print()
    print("CURRENT PROCESSING RESULTS")
    print("-" * 70)

    for result in results:

        if result["status"] == "new_version":

            data = result["data"]

            print(
                f"{result['document']} | "
                f"Version {result['version']} | "
                f"New Version"
            )

            print(
                f"  Products: {data['products']} | "
                f"Value: ₹{data['total_value']:.2f}"
            )

        elif result["status"] == "unchanged":

            data = result["data"]

            print(
                f"{result['document']} | "
                f"Version {result['version']} | "
                f"Unchanged - Skipped"
            )

            print(
                f"  Products: {data['products']} | "
                f"Value: ₹{data['total_value']:.2f}"
            )

        else:

            print(
                f"{result['document']} | "
                f"Failed | "
                f"{result['error']}"
            )

    print()
    print("VERSION HISTORY")
    print("-" * 70)

    for document, versions in history.items():

        print()
        print(
            f"{document} | "
            f"Total Versions: {len(versions)}"
        )

        for version in versions:

            data = version["data"]

            print(
                f"  Version {version['version']} | "
                f"Value: ₹{data['total_value']:.2f} | "
                f"Hash: {version['hash'][:12]} | "
                f"Time: {version['timestamp']}"
            )

    print()
    print("VERSIONING SUMMARY")
    print("-" * 70)

    new_versions = sum(
        1
        for result in results
        if result["status"] == "new_version"
    )

    unchanged = sum(
        1
        for result in results
        if result["status"] == "unchanged"
    )

    failed = sum(
        1
        for result in results
        if result["status"] == "failed"
    )

    total_versions = sum(
        len(versions)
        for versions in history.values()
    )

    print(
        f"Documents Checked     : "
        f"{len(results)}"
    )

    print(
        f"New Versions          : "
        f"{new_versions}"
    )

    print(
        f"Unchanged Documents   : "
        f"{unchanged}"
    )

    print(
        f"Failed Documents      : "
        f"{failed}"
    )

    print(
        f"Total Stored Versions : "
        f"{total_versions}"
    )

    print()
    print("Exercise 85 completed successfully.")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    logger.info(
        "Starting Exercise 85 - "
        "Document Processing with Versioning"
    )

    report = process_documents(
        DOCUMENTS
    )

    display_report(report)

    logger.info(
        "Exercise 85 completed successfully"
    )


if __name__ == "__main__":
    main()