import hashlib
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

logger = logging.getLogger("gram_swaram_deduplication")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DOCUMENTS = [
    "77_product_catalog_1.txt",
    "77_product_catalog_2.txt",
    "83_product_catalog_1_copy.txt",
]

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
    Calculate SHA-256 hash of a document's contents.
    """

    logger.info("Calculating document hash: %s", file_path)

    file_content = Path(file_path).read_bytes()

    document_hash = hashlib.sha256(file_content).hexdigest()

    logger.info(
        "Document hash calculated: %s | Hash: %s",
        file_path,
        document_hash[:12],
    )

    return document_hash


# ---------------------------------------------------------
# Product Catalog Parser
# ---------------------------------------------------------

def parse_product_catalog(file_path: str) -> Dict:
    """
    Parse a product catalog and calculate basic statistics.
    """

    logger.info("Reading document: %s", file_path)

    lines = Path(file_path).read_text(encoding="utf-8").splitlines()

    table_lines = [
        line.strip()
        for line in lines
        if "|" in line
    ]

    if len(table_lines) < 2:
        raise ValueError("Product table is missing.")

    headers = [
        header.strip()
        for header in table_lines[0].split("|")
    ]

    for required_column in REQUIRED_COLUMNS:
        if required_column not in headers:
            raise ValueError(
                f"Missing required column: {required_column}"
            )

    products = []

    for line in table_lines[1:]:
        values = [
            value.strip()
            for value in line.split("|")
        ]

        if len(values) != len(headers):
            continue

        row = dict(zip(headers, values))

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
        if product["availability"].lower() == "available"
    )

    out_of_stock = sum(
        1
        for product in products
        if product["availability"].lower() == "out of stock"
    )

    return {
        "file": file_path,
        "products": len(products),
        "total_value": total_value,
        "available": available_products,
        "out_of_stock": out_of_stock,
    }


# ---------------------------------------------------------
# Deduplication Processing
# ---------------------------------------------------------

def process_documents(
    documents: List[str],
) -> Dict:

    logger.info(
        "Starting deduplication for %d documents",
        len(documents),
    )

    seen_hashes = set()

    results = []
    duplicate_documents = []
    failed_documents = []

    for document in documents:

        logger.info(
            "Checking document: %s",
            document,
        )

        try:
            document_hash = calculate_document_hash(
                document
            )

            if document_hash in seen_hashes:

                logger.warning(
                    "Duplicate document detected: %s",
                    document,
                )

                duplicate_documents.append(document)

                continue

            seen_hashes.add(document_hash)

            logger.info(
                "New document detected. Processing: %s",
                document,
            )

            result = parse_product_catalog(document)

            results.append(result)

            logger.info(
                "Successfully processed: %s",
                document,
            )

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

    return {
        "results": results,
        "duplicates": duplicate_documents,
        "failed": failed_documents,
    }


# ---------------------------------------------------------
# Report
# ---------------------------------------------------------

def display_report(report: Dict) -> None:

    results = report["results"]
    duplicates = report["duplicates"]
    failed = report["failed"]

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
    print("DOCUMENT PROCESSING WITH DEDUPLICATION")
    print("=" * 70)

    print()
    print("SUCCESSFULLY PROCESSED DOCUMENTS")
    print("-" * 70)

    for result in results:
        print(
            f"{result['file']} | "
            f"Products: {result['products']} | "
            f"Value: ₹{result['total_value']:.2f}"
        )

    print()
    print("DUPLICATE DOCUMENTS")
    print("-" * 70)

    if duplicates:
        for document in duplicates:
            print(f"{document} | Duplicate - Skipped")
    else:
        print("No duplicate documents detected.")

    print()
    print("FAILED DOCUMENTS")
    print("-" * 70)

    if failed:
        for item in failed:
            print(
                f"{item['file']} | "
                f"Error: {item['error']}"
            )
    else:
        print("No failed documents.")

    print()
    print("DEDUPLICATION SUMMARY")
    print("-" * 70)

    print(
        f"Documents Received    : "
        f"{len(DOCUMENTS)}"
    )

    print(
        f"Documents Processed   : "
        f"{len(results)}"
    )

    print(
        f"Duplicate Documents   : "
        f"{len(duplicates)}"
    )

    print(
        f"Failed Documents      : "
        f"{len(failed)}"
    )

    print()
    print("DATA SUMMARY")
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
    print("Exercise 83 completed successfully.")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():

    logger.info(
        "Starting Exercise 83 - "
        "Document Processing with Deduplication"
    )

    report = process_documents(DOCUMENTS)

    display_report(report)

    logger.info(
        "Exercise 83 completed successfully"
    )


if __name__ == "__main__":
    main()