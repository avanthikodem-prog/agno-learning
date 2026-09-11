import logging
from pathlib import Path

from ollama import Client


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_document_table_extraction")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent

DOCUMENT_PATH = BASE_DIR / "71_sample_table.txt"

OLLAMA_HOST = "http://127.0.0.1:11434"
MODEL_NAME = "llama3.2"


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
# Detect table rows using Python
# ---------------------------------------------------------
def detect_table(document: str) -> dict:
    """Detect pipe-separated table data deterministically."""

    logger.info("Detecting table structure using Python")

    lines = [
        line.strip()
        for line in document.splitlines()
        if "|" in line
    ]

    if not lines:
        logger.warning("No table-like rows detected")
        return {
            "headers": [],
            "rows": [],
        }

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
        "Table detected: %d columns, %d data rows",
        len(headers),
        len(rows),
    )

    return {
        "headers": headers,
        "rows": rows,
    }


# ---------------------------------------------------------
# Validate table
# ---------------------------------------------------------
def validate_table(table: dict) -> None:
    """Validate the extracted table."""

    logger.info("Validating extracted table")

    headers = table["headers"]
    rows = table["rows"]

    if not headers:
        raise ValueError("No table headers detected")

    expected_columns = len(headers)

    invalid_rows = [
        index + 1
        for index, row in enumerate(rows)
        if len(row) != expected_columns
    ]

    if invalid_rows:
        logger.warning(
            "Rows with incorrect column counts: %s",
            invalid_rows,
        )
    else:
        logger.info(
            "All table rows contain %d columns",
            expected_columns,
        )


# ---------------------------------------------------------
# Extract semantic table information using Ollama
# ---------------------------------------------------------
def extract_semantic_table_info(document: str) -> str:
    """Ask Ollama to understand the table."""

    logger.info(
        "Sending table document to Ollama for semantic extraction"
    )

    client = Client(host=OLLAMA_HOST)

    prompt = f"""
You are a structured data extraction assistant.

Analyze ONLY the document provided below.

Extract the table information.

Return exactly these sections:

DOCUMENT TITLE:
Give the document title.

TABLE PURPOSE:
Explain what the table represents in one short sentence.

COLUMNS:
List all column names.

PRODUCT COUNT:
Give the number of products/data rows.

AVAILABLE PRODUCTS:
List the products whose Availability is "Available".

OUT OF STOCK PRODUCTS:
List the products whose Availability is "Out of Stock".

AGRICULTURE PRODUCTS:
List the products whose Category is "Agriculture".

GROCERY PRODUCTS:
List the products whose Category is "Grocery".

IMPORTANT RULES:
1. Use ONLY information present in the document.
2. Do not use outside knowledge.
3. Do not invent products or values.
4. Follow the exact section format.
5. Keep the response concise.

DOCUMENT:
----------------
{document}
----------------

DOCUMENT TITLE:
"""

    response = client.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        options={
            "temperature": 0,
        },
    )

    result = response["message"]["content"].strip()

    logger.info(
        "Semantic table extraction completed: %d characters",
        len(result),
    )

    return result


# ---------------------------------------------------------
# Validate semantic extraction
# ---------------------------------------------------------
def validate_semantic_output(result: str) -> None:
    """Check that expected semantic sections exist."""

    logger.info("Validating semantic table output")

    required_sections = [
        "DOCUMENT TITLE:",
        "TABLE PURPOSE:",
        "COLUMNS:",
        "PRODUCT COUNT:",
        "AVAILABLE PRODUCTS:",
        "OUT OF STOCK PRODUCTS:",
        "AGRICULTURE PRODUCTS:",
        "GROCERY PRODUCTS:",
    ]

    missing_sections = [
        section
        for section in required_sections
        if section not in result.upper()
    ]

    if missing_sections:
        logger.warning(
            "Missing semantic sections: %s",
            ", ".join(missing_sections),
        )
    else:
        logger.info(
            "All expected semantic sections are present"
        )


# ---------------------------------------------------------
# Display deterministic table
# ---------------------------------------------------------
def display_table(table: dict) -> None:
    """Display the table extracted by Python."""

    print("\n" + "=" * 70)
    print("DETERMINISTIC TABLE EXTRACTION")
    print("=" * 70)

    headers = table["headers"]
    rows = table["rows"]

    if not headers:
        print("No table detected.")
        return

    print("\nColumns:")

    for index, header in enumerate(headers, start=1):
        print(f"{index}. {header}")

    print("\nRows:")

    for index, row in enumerate(rows, start=1):
        print(f"{index}. " + " | ".join(row))

    print(f"\nTotal Columns : {len(headers)}")
    print(f"Total Rows    : {len(rows)}")


# ---------------------------------------------------------
# Display semantic information
# ---------------------------------------------------------
def display_semantic_output(result: str) -> None:
    """Display Ollama semantic extraction."""

    print("\n" + "=" * 70)
    print("SEMANTIC TABLE EXTRACTION")
    print("=" * 70)

    print(result)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    logger.info(
        "Starting Exercise 71 - Document Table/Data Extraction"
    )

    # Step 1: Read document
    document = read_document(DOCUMENT_PATH)

    # Step 2: Detect table using Python
    table = detect_table(document)

    # Step 3: Validate table
    validate_table(table)

    # Step 4: Display deterministic extraction
    display_table(table)

    # Step 5: Ask Ollama for semantic extraction
    semantic_result = extract_semantic_table_info(document)

    # Step 6: Validate semantic result
    validate_semantic_output(semantic_result)

    # Step 7: Display semantic extraction
    display_semantic_output(semantic_result)

    print("\n" + "=" * 70)
    print("Exercise 71 completed successfully.")
    print("=" * 70)

    logger.info("Exercise 71 completed successfully")


if __name__ == "__main__":
    main()