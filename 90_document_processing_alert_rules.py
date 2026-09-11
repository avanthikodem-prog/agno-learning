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

logger = logging.getLogger("gram_swaram_alert_rules")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

MONITORING_FILE = Path(
    "88_document_processing_monitoring.json"
)

ALERT_RULES_FILE = Path(
    "90_document_processing_alert_rules.json"
)


# ---------------------------------------------------------
# Alert Rules
# ---------------------------------------------------------

ALERT_RULES = [
    {
        "rule_id": "RULE-001",
        "rule_name": "High Failure Rate",
        "metric": "failure_rate_percent",
        "operator": ">=",
        "threshold": 20.0,
        "severity": "CRITICAL",
        "message": (
            "Critical document processing failure rate detected."
        ),
    },
    {
        "rule_id": "RULE-002",
        "rule_name": "Elevated Failure Rate",
        "metric": "failure_rate_percent",
        "operator": ">=",
        "threshold": 10.0,
        "severity": "WARNING",
        "message": (
            "Document processing failure rate is elevated."
        ),
    },
    {
        "rule_id": "RULE-003",
        "rule_name": "Processing Failures",
        "metric": "failed_events",
        "operator": ">",
        "threshold": 0,
        "severity": "WARNING",
        "message": (
            "One or more document processing failures detected."
        ),
    },
    {
        "rule_id": "RULE-004",
        "rule_name": "High Document Change Rate",
        "metric": "change_rate_percent",
        "operator": ">=",
        "threshold": 30.0,
        "severity": "WARNING",
        "message": (
            "Document change rate is unusually high."
        ),
    },
    {
        "rule_id": "RULE-005",
        "rule_name": "No Processing Events",
        "metric": "total_events",
        "operator": "==",
        "threshold": 0,
        "severity": "CRITICAL",
        "message": (
            "No document processing events were recorded."
        ),
    },
]


# ---------------------------------------------------------
# Load Monitoring Data
# ---------------------------------------------------------

def load_monitoring_data() -> dict:
    """Load monitoring data from Exercise 88."""

    if not MONITORING_FILE.exists():
        logger.error(
            "Monitoring file not found: %s",
            MONITORING_FILE,
        )

        raise FileNotFoundError(
            f"{MONITORING_FILE} was not found."
        )

    logger.info(
        "Loading monitoring data from %s",
        MONITORING_FILE,
    )

    with MONITORING_FILE.open(
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


# ---------------------------------------------------------
# Extract Metrics
# ---------------------------------------------------------

def extract_metrics(
    monitoring_data: dict,
) -> dict:
    """Extract metrics from Exercise 88 monitoring data."""

    monitoring = monitoring_data.get(
        "monitoring",
        {},
    )

    metrics = monitoring.get(
        "metrics",
        {},
    )

    extracted_metrics = {
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
        "failed_events": int(
            metrics.get(
                "failed_events",
                0,
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
        "success_rate_percent": float(
            metrics.get(
                "success_rate_percent",
                0.0,
            )
        ),
    }

    logger.info(
        "Extracted monitoring metrics successfully."
    )

    return extracted_metrics


# ---------------------------------------------------------
# Evaluate Rule
# ---------------------------------------------------------

def evaluate_rule(
    rule: dict,
    metrics: dict,
) -> bool:
    """Evaluate one alert rule against monitoring metrics."""

    metric_name = rule["metric"]
    operator = rule["operator"]
    threshold = rule["threshold"]

    value = metrics.get(
        metric_name,
        0,
    )

    if operator == ">":
        return value > threshold

    if operator == ">=":
        return value >= threshold

    if operator == "<":
        return value < threshold

    if operator == "<=":
        return value <= threshold

    if operator == "==":
        return value == threshold

    if operator == "!=":
        return value != threshold

    logger.warning(
        "Unsupported operator '%s' in rule %s",
        operator,
        rule["rule_id"],
    )

    return False


# ---------------------------------------------------------
# Generate Rule Results
# ---------------------------------------------------------

def evaluate_all_rules(
    metrics: dict,
) -> list[dict]:
    """Evaluate all configured alert rules."""

    results = []

    logger.info(
        "Evaluating %d alert rules.",
        len(ALERT_RULES),
    )

    for rule in ALERT_RULES:

        metric_name = rule["metric"]
        metric_value = metrics.get(
            metric_name,
            0,
        )

        triggered = evaluate_rule(
            rule,
            metrics,
        )

        result = {
            "rule_id": rule["rule_id"],
            "rule_name": rule["rule_name"],
            "metric": metric_name,
            "operator": rule["operator"],
            "threshold": rule["threshold"],
            "actual_value": metric_value,
            "severity": rule["severity"],
            "triggered": triggered,
            "message": rule["message"],
        }

        results.append(result)

        if triggered:
            logger.warning(
                "Rule triggered | %s | value=%s | threshold=%s",
                rule["rule_id"],
                metric_value,
                rule["threshold"],
            )

        else:
            logger.info(
                "Rule passed | %s | value=%s | threshold=%s",
                rule["rule_id"],
                metric_value,
                rule["threshold"],
            )

    return results


# ---------------------------------------------------------
# Save Results
# ---------------------------------------------------------

def save_results(
    metrics: dict,
    rule_results: list[dict],
) -> None:
    """Save alert rule evaluation results."""

    triggered_rules = [
        result
        for result in rule_results
        if result["triggered"]
    ]

    output = {
        "generated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "source": str(MONITORING_FILE),
        "metrics": metrics,
        "total_rules": len(rule_results),
        "triggered_rules": len(triggered_rules),
        "passed_rules": (
            len(rule_results)
            - len(triggered_rules)
        ),
        "rules": rule_results,
    }

    with ALERT_RULES_FILE.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            output,
            file,
            indent=4,
        )

    logger.info(
        "Alert rule results saved to %s",
        ALERT_RULES_FILE,
    )


# ---------------------------------------------------------
# Display Results
# ---------------------------------------------------------

def display_results(
    rule_results: list[dict],
) -> None:
    """Display alert rule evaluation results."""

    print("\n" + "=" * 75)
    print("DOCUMENT PROCESSING ALERT RULES")
    print("=" * 75)

    for result in rule_results:

        status = (
            "TRIGGERED"
            if result["triggered"]
            else "PASSED"
        )

        print(
            f"\n{result['rule_id']} - "
            f"{result['rule_name']}"
        )

        print("-" * 75)

        print(
            f"Metric       : {result['metric']}"
        )

        print(
            f"Actual Value : {result['actual_value']}"
        )

        print(
            f"Condition    : "
            f"{result['operator']} "
            f"{result['threshold']}"
        )

        print(
            f"Severity     : {result['severity']}"
        )

        print(
            f"Status       : {status}"
        )

        if result["triggered"]:
            print(
                f"Message      : {result['message']}"
            )

    triggered_count = sum(
        1
        for result in rule_results
        if result["triggered"]
    )

    print("\n" + "=" * 75)
    print(
        f"Total Rules      : {len(rule_results)}"
    )
    print(
        f"Triggered Rules  : {triggered_count}"
    )
    print(
        f"Passed Rules     : "
        f"{len(rule_results) - triggered_count}"
    )
    print("=" * 75)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main() -> None:
    """Run Exercise 90."""

    logger.info(
        "Starting Alert Rules & Thresholds"
    )

    try:

        monitoring_data = load_monitoring_data()

        metrics = extract_metrics(
            monitoring_data
        )

        rule_results = evaluate_all_rules(
            metrics
        )

        save_results(
            metrics,
            rule_results,
        )

        display_results(
            rule_results
        )

        logger.info(
            "Exercise 90 completed successfully."
        )

    except FileNotFoundError:
        logger.error(
            "Required monitoring file is missing."
        )

    except json.JSONDecodeError:
        logger.exception(
            "Monitoring JSON contains invalid JSON."
        )

    except Exception:
        logger.exception(
            "Unexpected error occurred during Exercise 90."
        )


if __name__ == "__main__":
    main()