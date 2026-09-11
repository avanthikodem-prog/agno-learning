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

logger = logging.getLogger("gram_swaram_document_classification")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
DOCUMENT_PATH = BASE_DIR / "sample_document.txt"

OLLAMA_HOST = "http://127.0.0.1:11434"
MODEL_NAME = "llama3.2"


# ---------------------------------------------------------
# Read document
# ---------------------------------------------------------
def read_document(file_path: Path) -> str:
    """Read the document from disk."""

    logger.info("Reading document: %s", file_path.name)

    if not file_path.exists():
        logger.error("Document not found: %s", file_path)
        raise FileNotFoundError(f"Document not found: {file_path}")

    text = file_path.read_text(encoding="utf-8")

    logger.info("Document loaded successfully: %d characters", len(text))

    return text


# ---------------------------------------------------------
# Clean document
# ---------------------------------------------------------
def clean_document(text: str) -> str:
    """Normalize whitespace and remove empty lines."""

    logger.info("Cleaning document text")

    lines = []

    for line in text.splitlines():
        line = " ".join(line.split())

        if line:
            lines.append(line)

    cleaned_text = "\n".join(lines)

    logger.info(
        "Document cleaning completed: %d characters",
        len(cleaned_text),
    )

    return cleaned_text


# ---------------------------------------------------------
# Classify document using Ollama
# ---------------------------------------------------------
def classify_document(document: str) -> str:
    """Classify the document into one of the predefined categories."""

    logger.info("Sending document to Ollama for classification")

    client = Client(host=OLLAMA_HOST)

    prompt = f"""
You are a document classification assistant.

Classify the document using ONLY the information contained
in the document.

Choose exactly ONE category from the following list:

1. Agriculture
2. E-Commerce
3. Technology
4. Education
5. Healthcare
6. Finance
7. Other

Return the result using EXACTLY this format:

CATEGORY: <one category>
CONFIDENCE: <High, Medium, or Low>
REASON: <one short sentence explaining the classification>

IMPORTANT RULES:
1. Choose only one category.
2. The category must come from the provided list.
3. Use only information present in the document.
4. Do not use outside knowledge.
5. Do not invent facts.
6. Keep the reason short and evidence-based.

DOCUMENT:
----------------
{document}
----------------

CATEGORY:
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
        "Document classification completed: %d characters",
        len(result),
    )

    return result


# ---------------------------------------------------------
# Validate classification
# ---------------------------------------------------------
def validate_classification(result: str) -> None:
    """Validate the basic structure of the classification result."""

    logger.info("Validating classification result")

    required_sections = [
        "CATEGORY:",
        "CONFIDENCE:",
        "REASON:",
    ]

    missing_sections = [
        section
        for section in required_sections
        if section not in result.upper()
    ]

    if missing_sections:
        logger.warning(
            "Missing expected sections: %s",
            ", ".join(missing_sections),
        )
    else:
        logger.info("All expected classification sections are present")

    valid_categories = {
        "AGRICULTURE",
        "E-COMMERCE",
        "TECHNOLOGY",
        "EDUCATION",
        "HEALTHCARE",
        "FINANCE",
        "OTHER",
    }

    category_line = ""

    for line in result.splitlines():
        if line.upper().startswith("CATEGORY:"):
            category_line = line.split(":", 1)[1].strip().upper()
            break

    if category_line in valid_categories:
        logger.info("Category validation passed: %s", category_line)
    else:
        logger.warning(
            "Unexpected category returned by model: %s",
            category_line or "Not found",
        )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    logger.info("Starting Exercise 68 - Document Classification")

    # Step 1: Read document
    raw_document = read_document(DOCUMENT_PATH)

    # Step 2: Clean document
    document = clean_document(raw_document)

    # Step 3: Classify document
    classification = classify_document(document)

    # Step 4: Validate result
    validate_classification(classification)

    # Step 5: Display result
    print("\n" + "=" * 70)
    print("DOCUMENT CLASSIFICATION")
    print("=" * 70)

    print("\nClassification Result:\n")
    print(classification)

    print("\n" + "=" * 70)
    print("Exercise 68 completed successfully.")
    print("=" * 70)

    logger.info("Exercise 68 completed successfully")


if __name__ == "__main__":
    main()