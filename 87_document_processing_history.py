import json
import logging
from pathlib import Path
from typing import Dict, List


# ============================================================
# LOGGING CONFIGURATION
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_history")


# ============================================================
# CONFIGURATION
# ============================================================

AUDIT_FILE = Path("86_document_audit_trail.json")
REPORT_FILE = Path("87_document_processing_history.json")


# ============================================================
# LOAD AUDIT TRAIL
# ============================================================

def load_audit_trail() -> Dict:
    """Load audit trail from JSON file."""

    logger.info(
        "Loading audit trail: %s",
        AUDIT_FILE,
    )

    if not AUDIT_FILE.exists():
        logger.error(
            "Audit trail file not found: %s",
            AUDIT_FILE,
        )
        raise FileNotFoundError(
            f"Required file not found: {AUDIT_FILE}"
        )

    with AUDIT_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    logger.info(
        "Audit trail loaded successfully | Events: %d",
        len(data.get("events", [])),
    )

    return data


# ============================================================
# BUILD DOCUMENT HISTORY
# ============================================================

def build_document_history(
    audit_data: Dict,
) -> Dict[str, List[Dict]]:
    """Group audit events by document."""

    logger.info(
        "Building document processing history"
    )

    history: Dict[str, List[Dict]] = {}

    for event in audit_data.get("events", []):

        document = event["document"]

        if document not in history:
            history[document] = []

        history[document].append(event)

    logger.info(
        "Document history created | Documents: %d",
        len(history),
    )

    return history


# ============================================================
# CREATE HISTORY SUMMARY
# ============================================================

def create_history_summary(
    document_history: Dict[str, List[Dict]],
) -> Dict:
    """Create a summary for each document."""

    logger.info(
        "Creating document history summary"
    )

    summary = {}

    for document, events in document_history.items():

        versions = []

        created_count = 0
        changed_count = 0
        checked_count = 0
        failed_count = 0

        for event in events:

            # Exercise 86 uses "event_type"
            event_type = event["event_type"]

            if event_type == "DOCUMENT_CREATED":
                created_count += 1

            elif event_type == "DOCUMENT_CHANGED":
                changed_count += 1

            elif event_type == "DOCUMENT_CHECKED":
                checked_count += 1

            elif event_type == "PROCESSING_FAILED":
                failed_count += 1

            version = event.get("version")

            if (
                version is not None
                and version not in versions
            ):
                versions.append(version)

        versions.sort()

        latest_event = events[-1]

        summary[document] = {
            "total_events": len(events),
            "versions": versions,
            "latest_version": latest_event.get(
                "version"
            ),
            "created_events": created_count,
            "changed_events": changed_count,
            "checked_events": checked_count,
            "failed_events": failed_count,
            "latest_status": latest_event.get(
                "status"
            ),
            "latest_event": latest_event.get(
                "event_type"
            ),
        }

    logger.info(
        "History summary created successfully"
    )

    return summary


# ============================================================
# SAVE HISTORY REPORT
# ============================================================

def save_history_report(
    summary: Dict,
) -> None:
    """Save document history report."""

    report = {
        "documents": summary,
        "total_documents": len(summary),
    }

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
        "History report saved successfully: %s",
        REPORT_FILE,
    )


# ============================================================
# DISPLAY HISTORY
# ============================================================

def display_history(
    summary: Dict,
) -> None:
    """Display document processing history."""

    print()
    print("=" * 75)
    print("DOCUMENT PROCESSING HISTORY")
    print("=" * 75)

    for document, data in summary.items():

        print()
        print(f"Document: {document}")
        print("-" * 75)

        print(
            f"Total Events     : "
            f"{data['total_events']}"
        )

        print(
            f"Versions         : "
            f"{data['versions']}"
        )

        print(
            f"Latest Version   : "
            f"{data['latest_version']}"
        )

        print(
            f"Created Events   : "
            f"{data['created_events']}"
        )

        print(
            f"Changed Events   : "
            f"{data['changed_events']}"
        )

        print(
            f"Checked Events   : "
            f"{data['checked_events']}"
        )

        print(
            f"Failed Events    : "
            f"{data['failed_events']}"
        )

        print(
            f"Latest Event     : "
            f"{data['latest_event']}"
        )

        print(
            f"Latest Status    : "
            f"{data['latest_status']}"
        )

    print()
    print("=" * 75)


# ============================================================
# DISPLAY EVENT TIMELINE
# ============================================================

def display_event_timeline(
    audit_data: Dict,
) -> None:
    """Display chronological audit event timeline."""

    events = audit_data.get("events", [])

    print()
    print("EVENT TIMELINE")
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
            f"   Event   : "
            f"{event['event_type']}"
        )

        print(
            f"   Version : "
            f"{event.get('version')}"
        )

        print(
            f"   Status  : "
            f"{event.get('status')}"
        )

        print(
            f"   Details : "
            f"{event.get('details')}"
        )

        print()


# ============================================================
# DISPLAY GLOBAL SUMMARY
# ============================================================

def display_global_summary(
    audit_data: Dict,
    summary: Dict,
) -> None:
    """Display overall history statistics."""

    events = audit_data.get("events", [])

    created = sum(
        1
        for event in events
        if event["event_type"]
        == "DOCUMENT_CREATED"
    )

    changed = sum(
        1
        for event in events
        if event["event_type"]
        == "DOCUMENT_CHANGED"
    )

    checked = sum(
        1
        for event in events
        if event["event_type"]
        == "DOCUMENT_CHECKED"
    )

    failed = sum(
        1
        for event in events
        if event["event_type"]
        == "PROCESSING_FAILED"
    )

    print()
    print("=" * 75)
    print("PROCESSING HISTORY SUMMARY")
    print("-" * 75)

    print(
        f"Documents            : "
        f"{len(summary)}"
    )

    print(
        f"Total Audit Events   : "
        f"{len(events)}"
    )

    print(
        f"Created Events       : "
        f"{created}"
    )

    print(
        f"Changed Events       : "
        f"{changed}"
    )

    print(
        f"Checked Events       : "
        f"{checked}"
    )

    print(
        f"Failed Events        : "
        f"{failed}"
    )

    print("=" * 75)


# ============================================================
# MAIN
# ============================================================

def main() -> None:
    """Run Exercise 87."""

    logger.info(
        "Starting Exercise 87 - Document Processing History"
    )

    try:

        audit_data = load_audit_trail()

        document_history = build_document_history(
            audit_data
        )

        summary = create_history_summary(
            document_history
        )

        save_history_report(summary)

        display_history(summary)

        display_event_timeline(
            audit_data
        )

        display_global_summary(
            audit_data,
            summary,
        )

        print()
        print(
            "Exercise 87 completed successfully."
        )

        logger.info(
            "Exercise 87 completed successfully"
        )

    except Exception as error:

        logger.exception(
            "Exercise 87 failed: %s",
            error,
        )

        print()
        print(
            f"Exercise 87 failed: {error}"
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()