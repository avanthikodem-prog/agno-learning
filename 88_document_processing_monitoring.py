import json
import logging
from pathlib import Path
from typing import Dict


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_monitoring")


# ============================================================
# CONFIGURATION
# ============================================================

AUDIT_FILE = Path("86_document_audit_trail.json")
REPORT_FILE = Path("88_document_processing_monitoring.json")


# ============================================================
# LOAD AUDIT TRAIL
# ============================================================

def load_audit_trail() -> Dict:
    """Load the document audit trail."""

    logger.info(
        "Loading audit trail: %s",
        AUDIT_FILE,
    )

    if not AUDIT_FILE.exists():
        raise FileNotFoundError(
            f"Audit trail not found: {AUDIT_FILE}"
        )

    with AUDIT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    logger.info(
        "Audit trail loaded | Events: %d",
        len(data.get("events", [])),
    )

    return data


# ============================================================
# CALCULATE MONITORING METRICS
# ============================================================

def calculate_metrics(
    audit_data: Dict,
) -> Dict:
    """Calculate document processing monitoring metrics."""

    logger.info("Calculating monitoring metrics")

    events = audit_data.get("events", [])

    total_events = len(events)

    created_events = 0
    changed_events = 0
    checked_events = 0
    failed_events = 0

    successful_events = 0

    documents = set()

    for event in events:

        documents.add(event["document"])

        event_type = event["event_type"]
        status = event.get("status")

        if event_type == "DOCUMENT_CREATED":
            created_events += 1

        elif event_type == "DOCUMENT_CHANGED":
            changed_events += 1

        elif event_type == "DOCUMENT_CHECKED":
            checked_events += 1

        elif event_type == "PROCESSING_FAILED":
            failed_events += 1

        if status == "SUCCESS":
            successful_events += 1

    if total_events > 0:
        success_rate = (
            successful_events
            / total_events
        ) * 100

        failure_rate = (
            failed_events
            / total_events
        ) * 100
    else:
        success_rate = 0.0
        failure_rate = 0.0

    if total_events > 0:
        change_rate = (
            changed_events
            / total_events
        ) * 100
    else:
        change_rate = 0.0

    metrics = {
        "total_documents": len(documents),
        "total_events": total_events,
        "created_events": created_events,
        "changed_events": changed_events,
        "checked_events": checked_events,
        "failed_events": failed_events,
        "successful_events": successful_events,
        "success_rate_percent": round(
            success_rate,
            2,
        ),
        "failure_rate_percent": round(
            failure_rate,
            2,
        ),
        "change_rate_percent": round(
            change_rate,
            2,
        ),
    }

    logger.info(
        "Monitoring metrics calculated successfully"
    )

    return metrics


# ============================================================
# DETERMINE SYSTEM HEALTH
# ============================================================

def determine_system_health(
    metrics: Dict,
) -> str:
    """Determine overall document processing health."""

    logger.info(
        "Determining document processing system health"
    )

    if metrics["total_events"] == 0:
        return "NO ACTIVITY"

    failure_rate = metrics[
        "failure_rate_percent"
    ]

    if failure_rate == 0:
        return "HEALTHY"

    if failure_rate < 20:
        return "WARNING"

    return "CRITICAL"


# ============================================================
# BUILD MONITORING REPORT
# ============================================================

def build_monitoring_report(
    metrics: Dict,
    health: str,
) -> Dict:
    """Build monitoring report."""

    report = {
        "monitoring": {
            "system_health": health,
            "metrics": metrics,
        }
    }

    return report


# ============================================================
# SAVE MONITORING REPORT
# ============================================================

def save_monitoring_report(
    report: Dict,
) -> None:
    """Save monitoring report to JSON."""

    with REPORT_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            report,
            file,
            indent=4,
            ensure_ascii=False,
        )

    logger.info(
        "Monitoring report saved: %s",
        REPORT_FILE,
    )


# ============================================================
# DISPLAY MONITORING DASHBOARD
# ============================================================

def display_monitoring_dashboard(
    metrics: Dict,
    health: str,
) -> None:
    """Display monitoring dashboard."""

    print()
    print("=" * 75)
    print("DOCUMENT PROCESSING MONITORING")
    print("=" * 75)

    print()
    print(
        f"System Health       : {health}"
    )

    print()
    print("PROCESSING METRICS")
    print("-" * 75)

    print(
        f"Total Documents     : "
        f"{metrics['total_documents']}"
    )

    print(
        f"Total Events        : "
        f"{metrics['total_events']}"
    )

    print(
        f"Successful Events   : "
        f"{metrics['successful_events']}"
    )

    print(
        f"Failed Events       : "
        f"{metrics['failed_events']}"
    )

    print(
        f"Created Events      : "
        f"{metrics['created_events']}"
    )

    print(
        f"Changed Events      : "
        f"{metrics['changed_events']}"
    )

    print(
        f"Checked Events      : "
        f"{metrics['checked_events']}"
    )

    print()
    print("RATES")
    print("-" * 75)

    print(
        f"Success Rate        : "
        f"{metrics['success_rate_percent']}%"
    )

    print(
        f"Failure Rate        : "
        f"{metrics['failure_rate_percent']}%"
    )

    print(
        f"Change Rate         : "
        f"{metrics['change_rate_percent']}%"
    )

    print()
    print("=" * 75)


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Run Exercise 88."""

    logger.info(
        "Starting Exercise 88 - Document Processing Monitoring"
    )

    try:

        audit_data = load_audit_trail()

        metrics = calculate_metrics(
            audit_data
        )

        health = determine_system_health(
            metrics
        )

        report = build_monitoring_report(
            metrics,
            health,
        )

        save_monitoring_report(
            report
        )

        display_monitoring_dashboard(
            metrics,
            health,
        )

        print()
        print(
            "Exercise 88 completed successfully."
        )

        logger.info(
            "Exercise 88 completed successfully"
        )

    except Exception as error:

        logger.exception(
            "Exercise 88 failed: %s",
            error,
        )

        print()
        print(
            f"Exercise 88 failed: {error}"
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()