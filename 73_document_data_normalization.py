import logging
import re
from pathlib import Path


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_document_data_normalization")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

DOCUMENT_PATH = BASE_DIR / "73_sample_data.txt"


# ---------------------------------------------------------
# Read document
# ---------------------------------------------------------
def read_document(file_path: Path) -> str:
    """Read the raw document."""

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
def parse_table(document: str) -> tuple[list[str], list[dict]]:
    """Parse the pipe-separated table."""

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
    raw_rows = parsed_rows[1:]

    rows = []

    for row in raw_rows:
        if len(row) != len(headers):
            logger.warning(
                "Skipping row with incorrect column count: %s",
                row,
            )
            continue

        rows.append(dict(zip(headers, row)))

    logger.info(
        "Parsed %d columns and %d data rows",
        len(headers),
        len(rows),
    )

    return headers, rows


# ---------------------------------------------------------
# Normalize product name
# ---------------------------------------------------------
def normalize_product(product: str) -> str:
    """Normalize product names."""

    value = product.strip()

    # Remove extra spaces
    value = re.sub(r"\s+", " ", value)

    # Convert to title case
    value = value.title()

    return value


# ---------------------------------------------------------
# Normalize price
# ---------------------------------------------------------
def normalize_price(price: str) -> str:
    """Normalize price into a numeric string."""

    value = price.strip()

    # Remove currency symbols and commas
    value = re.sub(r"[₹,$]", "", value)

    # Remove spaces
    value = value.replace(" ", "")

    # Convert to numeric value
    numeric_value = float(value)

    # Return integer-looking prices without .0
    if numeric_value.is_integer():
        return str(int(numeric_value))

    return str(numeric_value)


# ---------------------------------------------------------
# Normalize category
# ---------------------------------------------------------
def normalize_category(category: str) -> str:
    """Normalize category names."""

    value = category.strip()

    value = re.sub(r"\s+", " ", value)

    value = value.title()

    return value


# ---------------------------------------------------------
# Normalize availability
# ---------------------------------------------------------
def normalize_availability(availability: str) -> str:
    """Normalize availability values."""

    value = availability.strip().lower()

    if value == "available":
        return "Available"

    if value in {"out of stock", "out-of-stock", "outofstock"}:
        return "Out of Stock"

    return value.title()


# ---------------------------------------------------------
# Normalize complete table
# ---------------------------------------------------------
def normalize_table(rows: list[dict]) -> list[dict]:
    """Normalize all table values."""

    logger.info("Starting data normalization")

    normalized_rows = []

    for index, row in enumerate(rows, start=1):

        normalized_row = {
            "Product": normalize_product(row["Product"]),
            "Price": normalize_price(row["Price"]),
            "Category": normalize_category(row["Category"]),
            "Availability": normalize_availability(
                row["Availability"]
            ),
        }

        normalized_rows.append(normalized_row)

        logger.info(
            "Normalized row %d: %s",
            index,
            normalized_row,
        )

    logger.info(
        "Data normalization completed for %d rows",
        len(normalized_rows),
    )

    return normalized_rows


# ---------------------------------------------------------
# Display before normalization
# ---------------------------------------------------------
def display_raw_data(rows: list[dict]) -> None:
    """Display original data."""

    print("\n" + "=" * 80)
    print("RAW DATA")
    print("=" * 80)

    for index, row in enumerate(rows, start=1):
        print(
            f"{index}. "
            f"{row['Product']} | "
            f"{row['Price']} | "
            f"{row['Category']} | "
            f"{row['Availability']}"
        )


# ---------------------------------------------------------
# Display normalized data
# ---------------------------------------------------------
def display_normalized_data(rows: list[dict]) -> None:
    """Display normalized data."""

    print("\n" + "=" * 80)
    print("NORMALIZED DATA")
    print("=" * 80)

    for index, row in enumerate(rows, start=1):
        print(
            f"{index}. "
            f"{row['Product']} | "
            f"{row['Price']} | "
            f"{row['Category']} | "
            f"{row['Availability']}"
        )


# ---------------------------------------------------------
# Compare raw and normalized data
# ---------------------------------------------------------
def display_comparison(
    raw_rows: list[dict],
    normalized_rows: list[dict],
) -> None:
    """Show what changed during normalization."""

    print("\n" + "=" * 80)
    print("NORMALIZATION COMPARISON")
    print("=" * 80)

    for index, (raw, normalized) in enumerate(
        zip(raw_rows, normalized_rows),
        start=1,
    ):
        print(f"\nRow {index}:")

        print(
            f"Product      : "
            f"'{raw['Product']}' → '{normalized['Product']}'"
        )

        print(
            f"Price        : "
            f"'{raw['Price']}' → '{normalized['Price']}'"
        )

        print(
            f"Category     : "
            f"'{raw['Category']}' → '{normalized['Category']}'"
        )

        print(
            f"Availability : "
            f"'{raw['Availability']}' → "
            f"'{normalized['Availability']}'"
        )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    logger.info(
        "Starting Exercise 73 - Document Data Normalization"
    )

    # Step 1: Read document
    document = read_document(DOCUMENT_PATH)

    # Step 2: Parse table
    headers, raw_rows = parse_table(document)

    logger.info("Table headers: %s", headers)

    # Step 3: Display original data
    display_raw_data(raw_rows)

    # Step 4: Normalize data
    normalized_rows = normalize_table(raw_rows)

    # Step 5: Display normalized data
    display_normalized_data(normalized_rows)

    # Step 6: Display comparison
    display_comparison(
        raw_rows,
        normalized_rows,
    )

    print("\n" + "=" * 80)
    print("Exercise 73 completed successfully.")
    print("=" * 80)

    logger.info(
        "Exercise 73 completed successfully"
    )


if __name__ == "__main__":
    main()