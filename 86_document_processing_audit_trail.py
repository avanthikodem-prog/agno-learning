import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List


# =========================================================
# Logging Configuration
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_audit")


# =========================================================
# Configuration
# =========================================================

DOCUMENTS = [
    "77_product_catalog_1.txt",
    "77_product_catalog_2.txt",
]

AUDIT_FILE = Path("86_document_audit_trail.json")

REQUIRED_COLUMNS = [
    "Product",
    "Price",
    "Category",
    "Availability",
]


# =========================================================
# Timestamp
# =========================================================

def get_timestamp() -> str:
    """Return the current UTC timestamp."""

    return datetime.now(
        timezone.utc
    ).isoformat()


# =========================================================
# Hash Calculation
# =========================================================

def calculate_document_hash(
    file_path: str,
) -> str:
    """Calculate SHA-256 hash for a document."""

    logger.info(
        "Calculating hash: %s",
        file_path,
    )

    content = Path(file_path).read_bytes()

    document_hash = hashlib.sha256(
        content
    ).hexdigest()

    logger.info(
        "Hash calculated: %s | Hash: %s",
        file_path,
        document_hash[:12],
    )

    return document_hash


# =========================================================
# Load Audit Trail
# =========================================================

def load_audit_trail() -> Dict:
    """Load existing audit trail."""

    if not AUDIT_FILE.exists():

        logger.info(
            "No audit trail found. Starting fresh."
        )

        return {
            "documents": {},
            "events": [],
        }

    try:

        audit_data = json.loads(
            AUDIT_FILE.read_text(
                encoding="utf-8"
            )
        )

        logger.info(
            "Audit trail loaded successfully. "
            "Events: %d",
            len(audit_data.get("events", [])),
        )

        return audit_data

    except json.JSONDecodeError as error:

        logger.error(
            "Invalid audit trail file: %s",
            error,
        )

        return {
            "documents": {},
            "events": [],
        }


# =========================================================
# Save Audit Trail
# =========================================================

def save_audit_trail(
    audit_data: Dict,
) -> None:
    """Save audit trail to JSON."""

    AUDIT_FILE.write_text(
        json.dumps(
            audit_data,
            indent=4,
        ),
        encoding="utf-8",
    )

    logger.info(
        "Audit trail saved successfully."
    )


# =========================================================
# Add Audit Event
# =========================================================

def add_audit_event(
    audit_data: Dict,
    document: str,
    event_type: str,
    version: int,
    previous_hash: str | None,
    current_hash: str,
    status: str,
    details: str,
) -> None:
    """Record an event in the audit trail."""

    event = {
        "timestamp": get_timestamp(),
        "document": document,
        "event_type": event_type,
        "version": version,
        "previous_hash": previous_hash,
        "current_hash": current_hash,
        "status": status,
        "details": details,
    }

    audit_data["events"].append(event)

    logger.info(
        "Audit event recorded | "
        "Document: %s | "
        "Event: %s | "
        "Version: %d",
        document,
        event_type,
        version,
    )


# =========================================================
# Parse Product Catalog
# =========================================================

def parse_product_catalog(
    file_path: str,
) -> Dict:
    """Parse the product catalog."""

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

    available = sum(
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
        "available": available,
        "out_of_stock": out_of_stock,
    }


# =========================================================
# Process One Document
# =========================================================

def process_document(
    document: str,
    audit_data: Dict,
) -> Dict:
    """Detect document state and create an audit event."""

    logger.info(
        "Checking document: %s",
        document,
    )

    current_hash = calculate_document_hash(
        document
    )

    document_state = audit_data[
        "documents"
    ].get(document)

    # -----------------------------------------------------
    # First time seeing this document
    # -----------------------------------------------------

    if document_state is None:

        logger.info(
            "New document detected: %s",
            document,
        )

        data = parse_product_catalog(
            document
        )

        version = 1

        audit_data["documents"][
            document
        ] = {
            "current_version": version,
            "current_hash": current_hash,
        }

        add_audit_event(
            audit_data=audit_data,
            document=document,
            event_type="DOCUMENT_CREATED",
            version=version,
            previous_hash=None,
            current_hash=current_hash,
            status="SUCCESS",
            details=(
                "First version of document "
                "was processed."
            ),
        )

        return {
            "status": "new",
            "document": document,
            "version": version,
            "data": data,
        }

    # -----------------------------------------------------
    # Existing document
    # -----------------------------------------------------

    previous_hash = document_state[
        "current_hash"
    ]

    current_version = document_state[
        "current_version"
    ]

    # -----------------------------------------------------
    # Unchanged document
    # -----------------------------------------------------

    if current_hash == previous_hash:

        logger.info(
            "Document unchanged: %s | "
            "Version %d",
            document,
            current_version,
        )

        add_audit_event(
            audit_data=audit_data,
            document=document,
            event_type="DOCUMENT_CHECKED",
            version=current_version,
            previous_hash=previous_hash,
            current_hash=current_hash,
            status="UNCHANGED",
            details=(
                "Document was checked but "
                "no content change was detected."
            ),
        )

        return {
            "status": "unchanged",
            "document": document,
            "version": current_version,
        }

    # -----------------------------------------------------
    # Changed document
    # -----------------------------------------------------

    new_version = current_version + 1

    logger.info(
        "Document changed: %s | "
        "Version %d -> Version %d",
        document,
        current_version,
        new_version,
    )

    data = parse_product_catalog(
        document
    )

    audit_data["documents"][
        document
    ] = {
        "current_version": new_version,
        "current_hash": current_hash,
    }

    add_audit_event(
        audit_data=audit_data,
        document=document,
        event_type="DOCUMENT_CHANGED",
        version=new_version,
        previous_hash=previous_hash,
        current_hash=current_hash,
        status="SUCCESS",
        details=(
            "Document content changed and "
            "a new version was processed."
        ),
    )

    return {
        "status": "changed",
        "document": document,
        "version": new_version,
        "data": data,
    }


# =========================================================
# Process All Documents
# =========================================================

def process_documents(
    documents: List[str],
) -> Dict:

    audit_data = load_audit_trail()

    results = []

    for document in documents:

        try:

            result = process_document(
                document,
                audit_data,
            )

            results.append(result)

        except Exception as error:

            logger.error(
                "Failed to process %s: %s",
                document,
                error,
            )

            add_audit_event(
                audit_data=audit_data,
                document=document,
                event_type="PROCESSING_FAILED",
                version=0,
                previous_hash=None,
                current_hash="",
                status="FAILED",
                details=str(error),
            )

            results.append(
                {
                    "status": "failed",
                    "document": document,
                    "error": str(error),
                }
            )

    save_audit_trail(
        audit_data
    )

    return {
        "audit_data": audit_data,
        "results": results,
    }


# =========================================================
# Display Current Results
# =========================================================

def display_results(
    report: Dict,
) -> None:

    results = report["results"]

    print()
    print("=" * 75)
    print("DOCUMENT PROCESSING WITH AUDIT TRAIL")
    print("=" * 75)

    print()
    print("CURRENT PROCESSING RESULTS")
    print("-" * 75)

    for result in results:

        status = result["status"]

        if status == "new":

            data = result["data"]

            print(
                f"{result['document']} | "
                f"Version {result['version']} | "
                f"NEW DOCUMENT"
            )

            print(
                f"  Products: {data['products']} | "
                f"Value: ₹{data['total_value']:.2f}"
            )

        elif status == "changed":

            data = result["data"]

            print(
                f"{result['document']} | "
                f"Version {result['version']} | "
                f"CHANGED"
            )

            print(
                f"  Products: {data['products']} | "
                f"Value: ₹{data['total_value']:.2f}"
            )

        elif status == "unchanged":

            print(
                f"{result['document']} | "
                f"Version {result['version']} | "
                f"UNCHANGED"
            )

        else:

            print(
                f"{result['document']} | "
                f"FAILED | "
                f"{result['error']}"
            )


# =========================================================
# Display Audit Trail
# =========================================================

def display_audit_trail(
    audit_data: Dict,
) -> None:

    events = audit_data[
        "events"
    ]

    print()
    print("AUDIT TRAIL")
    print("-" * 75)

    for index, event in enumerate(
        events,
        start=1,
    ):

        print(
            f"{index}. "
            f"{event['timestamp']} | "
            f"{event['document']}"
        )

        print(
            f"   Event: {event['event_type']} | "
            f"Version: {event['version']} | "
            f"Status: {event['status']}"
        )

        previous_hash = event[
            "previous_hash"
        ]

        current_hash = event[
            "current_hash"
        ]

        previous_hash_display = (
            previous_hash[:12]
            if previous_hash
            else "None"
        )

        current_hash_display = (
            current_hash[:12]
            if current_hash
            else "None"
        )

        print(
            f"   Previous Hash: "
            f"{previous_hash_display}"
        )

        print(
            f"   Current Hash: "
            f"{current_hash_display}"
        )

        print(
            f"   Details: "
            f"{event['details']}"
        )

        print()


# =========================================================
# Display Summary
# =========================================================

def display_summary(
    report: Dict,
) -> None:

    results = report["results"]
    audit_data = report["audit_data"]

    new_documents = sum(
        1
        for result in results
        if result["status"] == "new"
    )

    changed_documents = sum(
        1
        for result in results
        if result["status"] == "changed"
    )

    unchanged_documents = sum(
        1
        for result in results
        if result["status"] == "unchanged"
    )

    failed_documents = sum(
        1
        for result in results
        if result["status"] == "failed"
    )

    total_events = len(
        audit_data["events"]
    )

    print("=" * 75)
    print("AUDIT TRAIL SUMMARY")
    print("-" * 75)

    print(
        f"Documents Checked     : "
        f"{len(results)}"
    )

    print(
        f"New Documents         : "
        f"{new_documents}"
    )

    print(
        f"Changed Documents     : "
        f"{changed_documents}"
    )

    print(
        f"Unchanged Documents   : "
        f"{unchanged_documents}"
    )

    print(
        f"Failed Documents      : "
        f"{failed_documents}"
    )

    print(
        f"Total Audit Events    : "
        f"{total_events}"
    )

    print()
    print(
        "Exercise 86 completed successfully."
    )


# =========================================================
# Main
# =========================================================

def main():

    logger.info(
        "Starting Exercise 86 - "
        "Document Processing with Audit Trail"
    )

    report = process_documents(
        DOCUMENTS
    )

    display_results(report)

    display_audit_trail(
        report["audit_data"]
    )

    display_summary(report)

    logger.info(
        "Exercise 86 completed successfully"
    )


if __name__ == "__main__":
    main()