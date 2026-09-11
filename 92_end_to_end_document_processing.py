import hashlib
import json
import logging
from datetime import datetime, timezone
from pathlib import Path


# ---------------------------------------------------------
# Logging Configuration
# ---------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger(
    "gram_swaram_end_to_end_processing"
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

DOCUMENTS = [
    Path("77_product_catalog_1.txt"),
    Path("77_product_catalog_2.txt"),
    Path("78_invalid_catalog.txt"),
]

STATE_FILE = Path(
    "92_document_processing_state.json"
)

REPORT_FILE = Path(
    "92_end_to_end_document_processing_report.json"
)

FAILURE_WARNING_THRESHOLD = 10.0
FAILURE_CRITICAL_THRESHOLD = 20.0


# ---------------------------------------------------------
# Load State
# ---------------------------------------------------------

def load_state() -> dict:
    """Load persistent processing state."""

    if not STATE_FILE.exists():
        logger.info(
            "No previous state found. Starting fresh."
        )

        return {
            "documents": {},
            "audit_events": [],
        }

    logger.info(
        "Loading processing state from %s",
        STATE_FILE,
    )

    with STATE_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


# ---------------------------------------------------------
# Save State
# ---------------------------------------------------------

def save_state(
    state: dict,
) -> None:
    """Save persistent processing state."""

    with STATE_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            state,
            file,
            indent=4,
        )

    logger.info(
        "Processing state saved."
    )


# ---------------------------------------------------------
# Calculate SHA-256 Hash
# ---------------------------------------------------------

def calculate_hash(
    file_path: Path,
) -> str:
    """Calculate SHA-256 hash of a document."""

    sha256 = hashlib.sha256()

    with file_path.open(
        "rb",
    ) as file:

        for chunk in iter(
            lambda: file.read(4096),
            b"",
        ):
            sha256.update(chunk)

    return sha256.hexdigest()


# ---------------------------------------------------------
# Parse Product Catalog
# ---------------------------------------------------------

def process_document(
    file_path: Path,
) -> dict:
    """
    Validate and process a product catalog.

    Expected columns:
    Product | Price | Category | Availability
    """

    logger.info(
        "Processing document: %s",
        file_path.name,
    )

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        lines = [
            line.strip()
            for line in file
            if line.strip()
        ]

    if len(lines) < 2:
        raise ValueError(
            "Document does not contain enough data."
        )

    # -----------------------------------------------------
    # Find the actual table header dynamically
    # -----------------------------------------------------

    required_columns = {
        "Product",
        "Price",
        "Category",
        "Availability",
    }

    header = None
    header_index = None

    for index, line in enumerate(lines):

        columns = [
            column.strip()
            for column in line.split("|")
        ]

        if required_columns.issubset(
            set(columns)
        ):
            header = columns
            header_index = index
            break

    if header is None:
        raise ValueError(
            "Missing required column(s): "
            "Product, Price, Category, Availability"
        )

    logger.info(
        "Header detected at line %d: %s",
        header_index + 1,
        " | ".join(header),
    )

    product_index = header.index(
        "Product"
    )

    price_index = header.index(
        "Price"
    )

    category_index = header.index(
        "Category"
    )

    availability_index = header.index(
        "Availability"
    )

    products = []

    total_value = 0.0
    available_count = 0
    out_of_stock_count = 0

    # -----------------------------------------------------
    # Process rows after the header
    # -----------------------------------------------------

    for line in lines[
        header_index + 1:
    ]:

        columns = [
            column.strip()
            for column in line.split("|")
        ]

        if len(columns) != len(header):
            raise ValueError(
                f"Invalid row format: {line}"
            )

        product_name = columns[
            product_index
        ]

        price_text = (
            columns[price_index]
            .replace("₹", "")
            .replace(",", "")
            .strip()
        )

        price = float(price_text)

        category = columns[
            category_index
        ].title()

        availability = columns[
            availability_index
        ].title()

        products.append(
            {
                "product": product_name,
                "price": price,
                "category": category,
                "availability": availability,
            }
        )

        total_value += price

        if availability == "Available":
            available_count += 1

        elif availability == "Out Of Stock":
            out_of_stock_count += 1

    logger.info(
        "Document processed successfully | "
        "products=%d | value=%.2f",
        len(products),
        total_value,
    )

    return {
        "product_count": len(products),
        "total_value": total_value,
        "available_count": available_count,
        "out_of_stock_count": out_of_stock_count,
        "products": products,
    }


# ---------------------------------------------------------
# Audit Event
# ---------------------------------------------------------

def add_audit_event(
    state: dict,
    document: str,
    event_type: str,
    status: str,
    version: int,
    previous_hash: str | None,
    current_hash: str,
    details: str,
) -> None:
    """Record an audit event."""

    event = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "document": document,
        "event_type": event_type,
        "status": status,
        "version": version,
        "previous_hash": previous_hash,
        "current_hash": current_hash,
        "details": details,
    }

    state["audit_events"].append(
        event
    )

    logger.info(
        "Audit event recorded | "
        "document=%s | event=%s",
        document,
        event_type,
    )


# ---------------------------------------------------------
# Process Documents
# ---------------------------------------------------------

def process_documents(
    state: dict,
) -> dict:
    """Run the complete document processing pipeline."""

    total_documents = len(DOCUMENTS)

    new_documents = 0
    changed_documents = 0
    unchanged_documents = 0
    failed_documents = 0

    total_products = 0
    total_value = 0.0
    total_available = 0
    total_out_of_stock = 0

    processing_results = []

    for file_path in DOCUMENTS:

        document_name = file_path.name

        if not file_path.exists():

            logger.error(
                "Document not found: %s",
                document_name,
            )

            failed_documents += 1

            processing_results.append(
                {
                    "document": document_name,
                    "status": "FAILED",
                    "reason": "Document not found",
                }
            )

            continue

        current_hash = calculate_hash(
            file_path
        )

        try:

            previous_data = state[
                "documents"
            ].get(
                document_name
            )

            # -------------------------------------------------
            # NEW DOCUMENT
            # -------------------------------------------------

            if previous_data is None:

                logger.info(
                    "NEW document detected: %s",
                    document_name,
                )

                result = process_document(
                    file_path
                )

                version = 1

                state["documents"][
                    document_name
                ] = {
                    "current_hash": current_hash,
                    "current_version": version,
                }

                add_audit_event(
                    state=state,
                    document=document_name,
                    event_type="DOCUMENT_CREATED",
                    status="SUCCESS",
                    version=version,
                    previous_hash=None,
                    current_hash=current_hash,
                    details=(
                        "First version processed "
                        "successfully."
                    ),
                )

                new_documents += 1
                status = "NEW"

            # -------------------------------------------------
            # UNCHANGED DOCUMENT
            # -------------------------------------------------

            elif (
                previous_data["current_hash"]
                == current_hash
            ):

                logger.info(
                    "UNCHANGED document: %s",
                    document_name,
                )

                unchanged_documents += 1

                add_audit_event(
                    state=state,
                    document=document_name,
                    event_type="DOCUMENT_CHECKED",
                    status="SUCCESS",
                    version=previous_data[
                        "current_version"
                    ],
                    previous_hash=current_hash,
                    current_hash=current_hash,
                    details=(
                        "Document unchanged; "
                        "processing skipped."
                    ),
                )

                processing_results.append(
                    {
                        "document": document_name,
                        "status": "UNCHANGED",
                        "version": previous_data[
                            "current_version"
                        ],
                    }
                )

                continue

            # -------------------------------------------------
            # CHANGED DOCUMENT
            # -------------------------------------------------

            else:

                logger.info(
                    "CHANGED document detected: %s",
                    document_name,
                )

                result = process_document(
                    file_path
                )

                previous_hash = (
                    previous_data["current_hash"]
                )

                version = (
                    previous_data[
                        "current_version"
                    ]
                    + 1
                )

                state["documents"][
                    document_name
                ] = {
                    "current_hash": current_hash,
                    "current_version": version,
                }

                add_audit_event(
                    state=state,
                    document=document_name,
                    event_type="DOCUMENT_CHANGED",
                    status="SUCCESS",
                    version=version,
                    previous_hash=previous_hash,
                    current_hash=current_hash,
                    details=(
                        "Changed document processed "
                        "successfully."
                    ),
                )

                changed_documents += 1
                status = "CHANGED"

            # -------------------------------------------------
            # Aggregate Business Data
            # -------------------------------------------------

            total_products += result[
                "product_count"
            ]

            total_value += result[
                "total_value"
            ]

            total_available += result[
                "available_count"
            ]

            total_out_of_stock += result[
                "out_of_stock_count"
            ]

            processing_results.append(
                {
                    "document": document_name,
                    "status": status,
                    "version": version,
                    "product_count": result[
                        "product_count"
                    ],
                    "total_value": result[
                        "total_value"
                    ],
                    "available_count": result[
                        "available_count"
                    ],
                    "out_of_stock_count": result[
                        "out_of_stock_count"
                    ],
                }
            )

        except Exception as error:

            logger.error(
                "Processing failed for %s: %s",
                document_name,
                error,
            )

            failed_documents += 1

            processing_results.append(
                {
                    "document": document_name,
                    "status": "FAILED",
                    "reason": str(error),
                }
            )

            previous_data = state[
                "documents"
            ].get(
                document_name,
                {},
            )

            add_audit_event(
                state=state,
                document=document_name,
                event_type="PROCESSING_FAILED",
                status="FAILED",
                version=previous_data.get(
                    "current_version",
                    0,
                ),
                previous_hash=previous_data.get(
                    "current_hash"
                ),
                current_hash=current_hash,
                details=str(error),
            )

    # ---------------------------------------------------------
    # Monitoring Metrics
    # ---------------------------------------------------------

    successful_documents = (
        total_documents
        - failed_documents
    )

    if total_documents > 0:

        success_rate = (
            successful_documents
            / total_documents
            * 100
        )

        failure_rate = (
            failed_documents
            / total_documents
            * 100
        )

    else:

        success_rate = 0.0
        failure_rate = 0.0

    if failure_rate >= FAILURE_CRITICAL_THRESHOLD:

        system_health = "CRITICAL"

    elif failure_rate >= FAILURE_WARNING_THRESHOLD:

        system_health = "WARNING"

    else:

        system_health = "HEALTHY"

    return {
        "total_documents": total_documents,
        "new_documents": new_documents,
        "changed_documents": changed_documents,
        "unchanged_documents": unchanged_documents,
        "failed_documents": failed_documents,
        "successful_documents": successful_documents,
        "success_rate_percent": success_rate,
        "failure_rate_percent": failure_rate,
        "system_health": system_health,
        "total_products": total_products,
        "total_value": total_value,
        "total_available": total_available,
        "total_out_of_stock": total_out_of_stock,
        "processing_results": processing_results,
    }


# ---------------------------------------------------------
# Generate Alerts
# ---------------------------------------------------------

def generate_alerts(
    summary: dict,
) -> list[dict]:
    """Generate alerts from processing metrics."""

    alerts = []

    failure_rate = summary[
        "failure_rate_percent"
    ]

    if failure_rate >= FAILURE_CRITICAL_THRESHOLD:

        alerts.append(
            {
                "severity": "CRITICAL",
                "alert_type": "HIGH_FAILURE_RATE",
                "message": (
                    "Critical document processing "
                    "failure rate detected."
                ),
                "value": failure_rate,
                "threshold": FAILURE_CRITICAL_THRESHOLD,
            }
        )

    elif failure_rate >= FAILURE_WARNING_THRESHOLD:

        alerts.append(
            {
                "severity": "WARNING",
                "alert_type": "ELEVATED_FAILURE_RATE",
                "message": (
                    "Document processing failure "
                    "rate is elevated."
                ),
                "value": failure_rate,
                "threshold": FAILURE_WARNING_THRESHOLD,
            }
        )

    elif summary[
        "failed_documents"
    ] > 0:

        alerts.append(
            {
                "severity": "WARNING",
                "alert_type": "PROCESSING_FAILURES",
                "message": (
                    "One or more documents failed "
                    "during processing."
                ),
                "value": summary[
                    "failed_documents"
                ],
                "threshold": 0,
            }
        )

    else:

        alerts.append(
            {
                "severity": "INFO",
                "alert_type": "SYSTEM_HEALTHY",
                "message": (
                    "End-to-end document processing "
                    "completed successfully."
                ),
                "value": 0,
                "threshold": 0,
            }
        )

    return alerts


# ---------------------------------------------------------
# Build Final Report
# ---------------------------------------------------------

def build_report(
    summary: dict,
    alerts: list[dict],
    state: dict,
) -> dict:
    """Build the final system report."""

    critical_alerts = sum(
        1
        for alert in alerts
        if alert["severity"] == "CRITICAL"
    )

    warning_alerts = sum(
        1
        for alert in alerts
        if alert["severity"] == "WARNING"
    )

    info_alerts = sum(
        1
        for alert in alerts
        if alert["severity"] == "INFO"
    )

    return {
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "system": {
            "name": (
                "GramSwaram Document Processing System"
            ),
            "status": summary[
                "system_health"
            ],
        },

        "processing_summary": {
            "total_documents": summary[
                "total_documents"
            ],
            "new_documents": summary[
                "new_documents"
            ],
            "changed_documents": summary[
                "changed_documents"
            ],
            "unchanged_documents": summary[
                "unchanged_documents"
            ],
            "successful_documents": summary[
                "successful_documents"
            ],
            "failed_documents": summary[
                "failed_documents"
            ],
        },

        "performance": {
            "success_rate_percent": summary[
                "success_rate_percent"
            ],
            "failure_rate_percent": summary[
                "failure_rate_percent"
            ],
        },

        "business_data": {
            "total_products": summary[
                "total_products"
            ],
            "total_value": summary[
                "total_value"
            ],
            "available_products": summary[
                "total_available"
            ],
            "out_of_stock_products": summary[
                "total_out_of_stock"
            ],
        },

        "alerts": {
            "total_alerts": len(alerts),
            "critical_alerts": critical_alerts,
            "warning_alerts": warning_alerts,
            "info_alerts": info_alerts,
            "details": alerts,
        },

        "audit": {
            "total_audit_events": len(
                state["audit_events"]
            ),
        },

        "documents": summary[
            "processing_results"
        ],
    }


# ---------------------------------------------------------
# Save Final Report
# ---------------------------------------------------------

def save_report(
    report: dict,
) -> None:
    """Save final report to JSON."""

    with REPORT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            report,
            file,
            indent=4,
        )

    logger.info(
        "Final report saved to %s",
        REPORT_FILE,
    )


# ---------------------------------------------------------
# Display Dashboard
# ---------------------------------------------------------

def display_report(
    report: dict,
) -> None:
    """Display the final end-to-end dashboard."""

    system = report["system"]
    summary = report[
        "processing_summary"
    ]
    performance = report[
        "performance"
    ]
    business = report[
        "business_data"
    ]
    alerts = report["alerts"]
    audit = report["audit"]

    print("\n" + "=" * 75)
    print(
        "GRAMSWARAM END-TO-END "
        "DOCUMENT PROCESSING SYSTEM"
    )
    print("=" * 75)

    print(
        f"\nSystem Status       : "
        f"{system['status']}"
    )

    print("\n" + "-" * 75)
    print("PROCESSING SUMMARY")
    print("-" * 75)

    print(
        f"Total Documents     : "
        f"{summary['total_documents']}"
    )

    print(
        f"New Documents       : "
        f"{summary['new_documents']}"
    )

    print(
        f"Changed Documents   : "
        f"{summary['changed_documents']}"
    )

    print(
        f"Unchanged Documents : "
        f"{summary['unchanged_documents']}"
    )

    print(
        f"Successful          : "
        f"{summary['successful_documents']}"
    )

    print(
        f"Failed              : "
        f"{summary['failed_documents']}"
    )

    print("\n" + "-" * 75)
    print("PERFORMANCE")
    print("-" * 75)

    print(
        f"Success Rate        : "
        f"{performance['success_rate_percent']:.1f}%"
    )

    print(
        f"Failure Rate        : "
        f"{performance['failure_rate_percent']:.1f}%"
    )

    print("\n" + "-" * 75)
    print("BUSINESS DATA")
    print("-" * 75)

    print(
        f"Total Products      : "
        f"{business['total_products']}"
    )

    print(
        f"Total Value         : "
        f"₹{business['total_value']:.2f}"
    )

    print(
        f"Available Products  : "
        f"{business['available_products']}"
    )

    print(
        f"Out Of Stock        : "
        f"{business['out_of_stock_products']}"
    )

    print("\n" + "-" * 75)
    print("ALERTS")
    print("-" * 75)

    print(
        f"Total Alerts        : "
        f"{alerts['total_alerts']}"
    )

    print(
        f"Critical Alerts     : "
        f"{alerts['critical_alerts']}"
    )

    print(
        f"Warning Alerts      : "
        f"{alerts['warning_alerts']}"
    )

    print(
        f"Info Alerts         : "
        f"{alerts['info_alerts']}"
    )

    print("\n" + "-" * 75)
    print("AUDIT")
    print("-" * 75)

    print(
        f"Audit Events        : "
        f"{audit['total_audit_events']}"
    )

    print("=" * 75)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main() -> None:
    """Run Exercise 92."""

    logger.info(
        "Starting End-to-End Document Processing System"
    )

    try:

        state = load_state()

        summary = process_documents(
            state
        )

        alerts = generate_alerts(
            summary
        )

        save_state(
            state
        )

        report = build_report(
            summary=summary,
            alerts=alerts,
            state=state,
        )

        save_report(
            report
        )

        display_report(
            report
        )

        logger.info(
            "Exercise 92 completed successfully."
        )

    except json.JSONDecodeError:
        logger.exception(
            "Processing state contains invalid JSON."
        )

    except Exception:
        logger.exception(
            "Unexpected error occurred during Exercise 92."
        )


if __name__ == "__main__":
    main()