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
    "gram_swaram_health_dashboard"
)


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

MONITORING_FILE = Path(
    "88_document_processing_monitoring.json"
)

ALERT_RULES_FILE = Path(
    "90_document_processing_alert_rules.json"
)

DASHBOARD_FILE = Path(
    "91_document_processing_health_dashboard.json"
)


# ---------------------------------------------------------
# Load JSON
# ---------------------------------------------------------

def load_json_file(
    file_path: Path,
) -> dict:
    """Load a JSON file."""

    if not file_path.exists():
        logger.error(
            "Required file not found: %s",
            file_path,
        )

        raise FileNotFoundError(
            f"{file_path} was not found."
        )

    logger.info(
        "Loading data from %s",
        file_path,
    )

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


# ---------------------------------------------------------
# Extract Monitoring Information
# ---------------------------------------------------------

def extract_monitoring(
    monitoring_data: dict,
) -> dict:
    """Extract monitoring information."""

    monitoring = monitoring_data.get(
        "monitoring",
        {},
    )

    metrics = monitoring.get(
        "metrics",
        {},
    )

    result = {
        "system_health": monitoring.get(
            "system_health",
            "UNKNOWN",
        ),
        "total_documents": int(
            metrics.get(
                "total_documents",
                0,
            )
        ),
        "total_events": int(
            metrics.get(
                "total_events",
                0,
            )
        ),
        "successful_events": int(
            metrics.get(
                "successful_events",
                0,
            )
        ),
        "failed_events": int(
            metrics.get(
                "failed_events",
                0,
            )
        ),
        "created_events": int(
            metrics.get(
                "created_events",
                0,
            )
        ),
        "changed_events": int(
            metrics.get(
                "changed_events",
                0,
            )
        ),
        "checked_events": int(
            metrics.get(
                "checked_events",
                0,
            )
        ),
        "success_rate_percent": float(
            metrics.get(
                "success_rate_percent",
                0.0,
            )
        ),
        "failure_rate_percent": float(
            metrics.get(
                "failure_rate_percent",
                0.0,
            )
        ),
        "change_rate_percent": float(
            metrics.get(
                "change_rate_percent",
                0.0,
            )
        ),
    }

    logger.info(
        "Monitoring information extracted successfully."
    )

    return result


# ---------------------------------------------------------
# Extract Rule Information
# ---------------------------------------------------------

def extract_rule_summary(
    rule_data: dict,
) -> dict:
    """Extract alert rule summary."""

    total_rules = int(
        rule_data.get(
            "total_rules",
            0,
        )
    )

    triggered_rules = int(
        rule_data.get(
            "triggered_rules",
            0,
        )
    )

    passed_rules = int(
        rule_data.get(
            "passed_rules",
            0,
        )
    )

    rules = rule_data.get(
        "rules",
        [],
    )

    critical_triggered = sum(
        1
        for rule in rules
        if rule.get("triggered")
        and rule.get("severity") == "CRITICAL"
    )

    warning_triggered = sum(
        1
        for rule in rules
        if rule.get("triggered")
        and rule.get("severity") == "WARNING"
    )

    result = {
        "total_rules": total_rules,
        "triggered_rules": triggered_rules,
        "passed_rules": passed_rules,
        "critical_triggered": critical_triggered,
        "warning_triggered": warning_triggered,
    }

    logger.info(
        "Alert rule summary extracted successfully."
    )

    return result


# ---------------------------------------------------------
# Determine Dashboard Status
# ---------------------------------------------------------

def determine_dashboard_status(
    system_health: str,
    critical_rules: int,
    warning_rules: int,
) -> str:
    """Determine overall dashboard status."""

    if (
        system_health == "CRITICAL"
        or critical_rules > 0
    ):
        return "CRITICAL"

    if (
        system_health == "WARNING"
        or warning_rules > 0
    ):
        return "WARNING"

    if system_health == "HEALTHY":
        return "HEALTHY"

    return "UNKNOWN"


# ---------------------------------------------------------
# Generate Recommendations
# ---------------------------------------------------------

def generate_recommendations(
    monitoring: dict,
    rule_summary: dict,
    dashboard_status: str,
) -> list[str]:
    """Generate recommendations based on system state."""

    recommendations = []

    if dashboard_status == "HEALTHY":
        recommendations.append(
            "Continue normal document processing monitoring."
        )

    if monitoring["failed_events"] > 0:
        recommendations.append(
            "Investigate failed document processing events."
        )

    if monitoring["failure_rate_percent"] >= 10.0:
        recommendations.append(
            "Review document processing failures "
            "and retry behavior."
        )

    if monitoring["change_rate_percent"] >= 30.0:
        recommendations.append(
            "Investigate the unusually high document "
            "change rate."
        )

    if rule_summary["critical_triggered"] > 0:
        recommendations.append(
            "Immediately investigate critical alert rules."
        )

    if rule_summary["warning_triggered"] > 0:
        recommendations.append(
            "Review warning-level alert rules."
        )

    if not recommendations:
        recommendations.append(
            "No immediate action is required."
        )

    return recommendations


# ---------------------------------------------------------
# Build Dashboard
# ---------------------------------------------------------

def build_dashboard(
    monitoring: dict,
    rule_summary: dict,
) -> dict:
    """Build complete health dashboard."""

    dashboard_status = determine_dashboard_status(
        system_health=monitoring["system_health"],
        critical_rules=rule_summary[
            "critical_triggered"
        ],
        warning_rules=rule_summary[
            "warning_triggered"
        ],
    )

    recommendations = generate_recommendations(
        monitoring=monitoring,
        rule_summary=rule_summary,
        dashboard_status=dashboard_status,
    )

    dashboard = {
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "dashboard": {
            "status": dashboard_status,

            "system_health": monitoring[
                "system_health"
            ],

            "document_metrics": {
                "total_documents": monitoring[
                    "total_documents"
                ],
                "total_events": monitoring[
                    "total_events"
                ],
                "successful_events": monitoring[
                    "successful_events"
                ],
                "failed_events": monitoring[
                    "failed_events"
                ],
            },

            "event_breakdown": {
                "created": monitoring[
                    "created_events"
                ],
                "changed": monitoring[
                    "changed_events"
                ],
                "checked": monitoring[
                    "checked_events"
                ],
            },

            "performance": {
                "success_rate_percent": monitoring[
                    "success_rate_percent"
                ],
                "failure_rate_percent": monitoring[
                    "failure_rate_percent"
                ],
                "change_rate_percent": monitoring[
                    "change_rate_percent"
                ],
            },

            "alert_rules": {
                "total_rules": rule_summary[
                    "total_rules"
                ],
                "triggered_rules": rule_summary[
                    "triggered_rules"
                ],
                "passed_rules": rule_summary[
                    "passed_rules"
                ],
                "critical_triggered": rule_summary[
                    "critical_triggered"
                ],
                "warning_triggered": rule_summary[
                    "warning_triggered"
                ],
            },

            "recommendations": recommendations,
        },
    }

    logger.info(
        "Health dashboard built successfully."
    )

    return dashboard


# ---------------------------------------------------------
# Save Dashboard
# ---------------------------------------------------------

def save_dashboard(
    dashboard: dict,
) -> None:
    """Save dashboard to JSON."""

    with DASHBOARD_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            dashboard,
            file,
            indent=4,
        )

    logger.info(
        "Dashboard saved to %s",
        DASHBOARD_FILE,
    )


# ---------------------------------------------------------
# Display Dashboard
# ---------------------------------------------------------

def display_dashboard(
    dashboard: dict,
) -> None:
    """Display dashboard in terminal."""

    data = dashboard["dashboard"]

    print("\n" + "=" * 75)
    print("GRAMSWARAM DOCUMENT PROCESSING HEALTH DASHBOARD")
    print("=" * 75)

    print(
        f"\nOverall Status      : "
        f"{data['status']}"
    )

    print(
        f"System Health       : "
        f"{data['system_health']}"
    )

    print("\n" + "-" * 75)
    print("DOCUMENT METRICS")
    print("-" * 75)

    metrics = data["document_metrics"]

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

    print("\n" + "-" * 75)
    print("EVENT BREAKDOWN")
    print("-" * 75)

    events = data["event_breakdown"]

    print(
        f"Created Events      : "
        f"{events['created']}"
    )

    print(
        f"Changed Events      : "
        f"{events['changed']}"
    )

    print(
        f"Checked Events      : "
        f"{events['checked']}"
    )

    print("\n" + "-" * 75)
    print("PERFORMANCE")
    print("-" * 75)

    performance = data["performance"]

    print(
        f"Success Rate        : "
        f"{performance['success_rate_percent']:.1f}%"
    )

    print(
        f"Failure Rate        : "
        f"{performance['failure_rate_percent']:.1f}%"
    )

    print(
        f"Change Rate         : "
        f"{performance['change_rate_percent']:.1f}%"
    )

    print("\n" + "-" * 75)
    print("ALERT RULES")
    print("-" * 75)

    rules = data["alert_rules"]

    print(
        f"Total Rules         : "
        f"{rules['total_rules']}"
    )

    print(
        f"Triggered Rules     : "
        f"{rules['triggered_rules']}"
    )

    print(
        f"Passed Rules        : "
        f"{rules['passed_rules']}"
    )

    print(
        f"Critical Rules      : "
        f"{rules['critical_triggered']}"
    )

    print(
        f"Warning Rules       : "
        f"{rules['warning_triggered']}"
    )

    print("\n" + "-" * 75)
    print("RECOMMENDATIONS")
    print("-" * 75)

    for index, recommendation in enumerate(
        data["recommendations"],
        start=1,
    ):
        print(
            f"{index}. {recommendation}"
        )

    print("=" * 75)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main() -> None:
    """Run Exercise 91."""

    logger.info(
        "Starting Document Processing Health Dashboard"
    )

    try:
        monitoring_data = load_json_file(
            MONITORING_FILE
        )

        rule_data = load_json_file(
            ALERT_RULES_FILE
        )

        monitoring = extract_monitoring(
            monitoring_data
        )

        rule_summary = extract_rule_summary(
            rule_data
        )

        dashboard = build_dashboard(
            monitoring=monitoring,
            rule_summary=rule_summary,
        )

        save_dashboard(
            dashboard
        )

        display_dashboard(
            dashboard
        )

        logger.info(
            "Exercise 91 completed successfully."
        )

    except FileNotFoundError:
        logger.error(
            "Required input file is missing."
        )

    except json.JSONDecodeError:
        logger.exception(
            "One of the JSON files contains invalid JSON."
        )

    except Exception:
        logger.exception(
            "Unexpected error occurred during Exercise 91."
        )


if __name__ == "__main__":
    main()