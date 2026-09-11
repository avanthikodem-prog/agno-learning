import logging
import re
from pathlib import Path

from ollama import Client


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_keyword_extraction")


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
# Extract information using Ollama
# ---------------------------------------------------------
def extract_information(document: str) -> str:
    """Ask Ollama to extract structured information from the document."""

    logger.info("Sending document to Ollama for information extraction")

    client = Client(host=OLLAMA_HOST)

    prompt = f"""
You are a document information extraction assistant.

Analyze ONLY the document provided below.

Extract the following information:

KEYWORDS:
List 5 to 10 important keywords from the document.

MAIN TOPICS:
List 3 to 5 main topics discussed in the document.

ORGANIZATIONS OR NAMED ENTITIES:
List organizations, platforms, products, or named entities explicitly
mentioned in the document.
If none are present, write "None".

TECHNOLOGIES OR CONCEPTS:
List technologies, technical concepts, or important digital concepts
explicitly mentioned in the document.
If none are present, write "None".

IMPORTANT RULES:
1. Use ONLY information present in the document.
2. Do not add outside knowledge.
3. Do not invent organizations, technologies, or entities.
4. Keep the output concise.
5. Follow the exact section format requested above.

DOCUMENT:
----------------
{document}
----------------

KEYWORDS:
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
        "Information extraction completed: %d characters",
        len(result),
    )

    return result


# ---------------------------------------------------------
# Validate extracted sections
# ---------------------------------------------------------
def validate_result(result: str) -> None:
    """Perform simple structural validation of the LLM output."""

    logger.info("Validating extracted information")

    required_sections = [
        "KEYWORDS",
        "MAIN TOPICS",
        "ORGANIZATIONS OR NAMED ENTITIES",
        "TECHNOLOGIES OR CONCEPTS",
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
        logger.info("All expected sections are present")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    logger.info("Starting Exercise 67 - Document Keyword Extraction")

    # Step 1: Read document
    raw_document = read_document(DOCUMENT_PATH)

    # Step 2: Clean document
    document = clean_document(raw_document)

    # Step 3: Extract information
    extracted_information = extract_information(document)

    # Step 4: Validate result
    validate_result(extracted_information)

    # Step 5: Display result
    print("\n" + "=" * 70)
    print("DOCUMENT KEYWORD & ENTITY EXTRACTION")
    print("=" * 70)

    print("\nExtracted Information:\n")
    print(extracted_information)

    print("\n" + "=" * 70)
    print("Exercise 67 completed successfully.")
    print("=" * 70)

    logger.info("Exercise 67 completed successfully")


if __name__ == "__main__":
    main()