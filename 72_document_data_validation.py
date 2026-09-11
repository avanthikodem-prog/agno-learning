import logging
from pathlib import Path


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_document_data_validation")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

DOCUMENT_PATH = BASE_DIR / "71_sample_table.txt"


# ---------------------------------------------------------
# Read document
# ---------------------------------------------------------
def read_document(file_path: Path) -> str:
    """Read the table document."""

    logger.info("Reading document: %s", file_path.name)

    if not file_path.exists():
        logger.error("Document not found: %s", file_path)
        raise FileNotFoundError(f"Document not found: {file_path}")

    text = file_path.read_text(encoding="utf-8")

    logger.info(
        "Document loaded successfully: %d characters",
        len(text),
    )

    return text


# ---------------------------------------------------------
# Parse table
# ---------------------------------------------------------
def parse_table(document: str) -> dict:
    """Convert the pipe-separated table into Python data."""

    logger.info("Parsing table data")

    lines = [
        line.strip()
        for line in document.splitlines()
        if "|" in line
    ]

    if not lines:
        raise ValueError("No table data found")

    parsed_rows = []

    for line in lines:
        columns = [
            column.strip()
            for column in line.split("|")
        ]

        parsed_rows.append(columns)

    headers = parsed_rows[0]
    rows = parsed_rows[1:]

    logger.info(
        "Parsed %d columns and %d data rows",
        len(headers),
        len(rows),
    )

    table_rows = []

    for row in rows:
        if len(row) != len(headers):
            logger.warning(
                "Skipping row with incorrect column count: %s",
                row,
            )
            continue

        table_rows.append(
            dict(zip(headers, row))
        )

    logger.info(
        "Successfully converted %d rows into dictionaries",
        len(table_rows),
    )

    return {
        "headers": headers,
        "rows": table_rows,
    }


# ---------------------------------------------------------
# Validate column structure
# ---------------------------------------------------------
def validate_columns(table: dict) -> list[str]:
    """Validate required columns."""

    logger.info("Validating table columns")

    required_columns = [
        "Product",
        "Price",
        "Category",
        "Availability",
    ]

    headers = table["headers"]

    errors = []

    for column in required_columns:
        if column not in headers:
            errors.append(
                f"Missing required column: {column}"
            )

    if errors:
        logger.warning(
            "Column validation found %d error(s)",
            len(errors),
        )
    else:
        logger.info("All required columns are present")

    return errors


# ---------------------------------------------------------
# Validate product names
# ---------------------------------------------------------
def validate_products(table: dict) -> list[str]:
    """Check product names."""

    logger.info("Validating product names")

    errors = []

    for index, row in enumerate(table["rows"], start=1):
        product = row["Product"].strip()

        if not product:
            errors.append(
                f"Row {index}: Product name is empty"
            )

    if errors:
        logger.warning(
            "Product validation found %d error(s)",
            len(errors),
        )
    else:
        logger.info("All product names are valid")

    return errors


# ---------------------------------------------------------
# Validate prices
# ---------------------------------------------------------
def validate_prices(table: dict) -> list[str]:
    """Check that prices are valid positive numbers."""

    logger.info("Validating product prices")

    errors = []

    for index, row in enumerate(table["rows"], start=1):
        product = row["Product"]
        price_text = row["Price"]

        try:
            price = float(price_text)

            if price <= 0:
                errors.append(
                    f"Row {index}: {product} has invalid price: {price_text}"
                )

        except ValueError:
            errors.append(
                f"Row {index}: {product} has non-numeric price: {price_text}"
            )

    if errors:
        logger.warning(
            "Price validation found %d error(s)",
            len(errors),
        )
    else:
        logger.info("All prices are valid")

    return errors


# ---------------------------------------------------------
# Validate categories
# ---------------------------------------------------------
def validate_categories(table: dict) -> list[str]:
    """Check that categories are allowed."""

    logger.info("Validating product categories")

    allowed_categories = {
        "Grocery",
        "Agriculture",
    }

    errors = []

    for index, row in enumerate(table["rows"], start=1):
        category = row["Category"]

        if category not in allowed_categories:
            errors.append(
                f"Row {index}: {row['Product']} has invalid category: {category}"
            )

    if errors:
        logger.warning(
            "Category validation found %d error(s)",
            len(errors),
        )
    else:
        logger.info("All categories are valid")

    return errors


# ---------------------------------------------------------
# Validate availability
# ---------------------------------------------------------
def validate_availability(table: dict) -> list[str]:
    """Check that availability values are allowed."""

    logger.info("Validating product availability")

    allowed_values = {
        "Available",
        "Out of Stock",
    }

    errors = []

    for index, row in enumerate(table["rows"], start=1):
        availability = row["Availability"]

        if availability not in allowed_values:
            errors.append(
                f"Row {index}: {row['Product']} has invalid availability: {availability}"
            )

    if errors:
        logger.warning(
            "Availability validation found %d error(s)",
            len(errors),
        )
    else:
        logger.info("All availability values are valid")

    return errors


# ---------------------------------------------------------
# Validate duplicate products
# ---------------------------------------------------------
def validate_duplicates(table: dict) -> list[str]:
    """Check for duplicate product names."""

    logger.info("Checking for duplicate products")

    seen = set()
    duplicates = []

    for row in table["rows"]:
        product = row["Product"]

        if product in seen:
            duplicates.append(
                f"Duplicate product: {product}"
            )
        else:
            seen.add(product)

    if duplicates:
        logger.warning(
            "Duplicate validation found %d duplicate(s)",
            len(duplicates),
        )
    else:
        logger.info("No duplicate products found")

    return duplicates


# ---------------------------------------------------------
# Display validation report
# ---------------------------------------------------------
def display_validation_report(errors: list[str]) -> None:
    """Display final validation results."""

    print("\n" + "=" * 70)
    print("DOCUMENT DATA VALIDATION REPORT")
    print("=" * 70)

    if not errors:
        print("\nSTATUS: VALID")
        print("\nAll document data passed validation.")
        return

    print("\nSTATUS: INVALID")

    print("\nValidation Errors:")

    for index, error in enumerate(errors, start=1):
        print(f"{index}. {error}")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    logger.info(
        "Starting Exercise 72 - Document Data Validation"
    )

    # Step 1: Read document
    document = read_document(DOCUMENT_PATH)

    # Step 2: Parse table
    table = parse_table(document)

    # Step 3: Validate columns
    all_errors = validate_columns(table)

    # Stop row validation if required columns are missing
    required_columns_present = not all_errors

    if required_columns_present:

        # Step 4: Validate products
        all_errors.extend(
            validate_products(table)
        )

        # Step 5: Validate prices
        all_errors.extend(
            validate_prices(table)
        )

        # Step 6: Validate categories
        all_errors.extend(
            validate_categories(table)
        )

        # Step 7: Validate availability
        all_errors.extend(
            validate_availability(table)
        )

        # Step 8: Validate duplicates
        all_errors.extend(
            validate_duplicates(table)
        )

    # Step 9: Display final report
    display_validation_report(all_errors)

    print("\n" + "=" * 70)
    print("Exercise 72 completed successfully.")
    print("=" * 70)

    logger.info(
        "Exercise 72 completed successfully"
    )


if __name__ == "__main__":
    main()