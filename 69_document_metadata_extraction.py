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

logger = logging.getLogger("gram_swaram_document_metadata")


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
# Calculate deterministic metadata
# ---------------------------------------------------------
def calculate_metadata(document: str, file_path: Path) -> dict:
    """Calculate metadata directly from the document."""

    logger.info("Calculating deterministic document metadata")

    words = re.findall(r"\b[\w'-]+\b", document)
    sentences = re.split(r"(?<=[.!?])\s+", document.strip())

    metadata = {
        "document_name": file_path.name,
        "document_type": file_path.suffix.lower().replace(".", "").upper()
        or "UNKNOWN",
        "character_count": len(document),
        "word_count": len(words),
        "line_count": len(document.splitlines()),
        "sentence_count": len(
            [sentence for sentence in sentences if sentence.strip()]
        ),
    }

    logger.info(
        "Metadata calculated: %d words, %d sentences",
        metadata["word_count"],
        metadata["sentence_count"],
    )

    return metadata


# ---------------------------------------------------------
# Extract semantic metadata using Ollama
# ---------------------------------------------------------
def extract_semantic_metadata(document: str) -> str:
    """Ask Ollama to extract semantic metadata from the document."""

    logger.info("Sending document to Ollama for semantic metadata extraction")

    client = Client(host=OLLAMA_HOST)

    prompt = f"""
You are a document metadata extraction assistant.

Analyze ONLY the document provided below.

Extract the following semantic metadata:

TITLE:
Give a short descriptive title for the document.

MAIN SUBJECT:
Give the main subject of the document in one short phrase.

LANGUAGE:
Identify the language used in the document.

CATEGORY:
Choose exactly ONE category:
- Agriculture
- E-Commerce
- Technology
- Education
- Healthcare
- Finance
- Other

KEYWORDS:
List 5 important keywords from the document.

NAMED ENTITIES:
List important named entities explicitly mentioned in the document.
If there are none, write "None".

IMPORTANT RULES:
1. Use ONLY information present in the document.
2. Do not use outside knowledge.
3. Do not invent facts.
4. Keep the output concise.
5. Follow the exact section format.

DOCUMENT:
----------------
{document}
----------------

TITLE:
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
        "Semantic metadata extraction completed: %d characters",
        len(result),
    )

    return result


# ---------------------------------------------------------
# Validate semantic metadata
# ---------------------------------------------------------
def validate_semantic_metadata(result: str) -> None:
    """Validate the expected metadata sections."""

    logger.info("Validating semantic metadata")

    required_sections = [
        "TITLE:",
        "MAIN SUBJECT:",
        "LANGUAGE:",
        "CATEGORY:",
        "KEYWORDS:",
        "NAMED ENTITIES:",
    ]

    missing_sections = [
        section
        for section in required_sections
        if section not in result.upper()
    ]

    if missing_sections:
        logger.warning(
            "Missing expected metadata sections: %s",
            ", ".join(missing_sections),
        )
    else:
        logger.info("All expected semantic metadata sections are present")


# ---------------------------------------------------------
# Display metadata
# ---------------------------------------------------------
def display_metadata(deterministic_metadata: dict, semantic_metadata: str) -> None:
    """Display the complete document metadata."""

    print("\n" + "=" * 70)
    print("DOCUMENT METADATA")
    print("=" * 70)

    print("\nDeterministic Metadata:")
    print(f"Document Name   : {deterministic_metadata['document_name']}")
    print(f"Document Type   : {deterministic_metadata['document_type']}")
    print(f"Character Count : {deterministic_metadata['character_count']}")
    print(f"Word Count      : {deterministic_metadata['word_count']}")
    print(f"Line Count      : {deterministic_metadata['line_count']}")
    print(f"Sentence Count  : {deterministic_metadata['sentence_count']}")

    print("\nSemantic Metadata:")
    print(semantic_metadata)

    print("\n" + "=" * 70)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    logger.info("Starting Exercise 69 - Document Metadata Extraction")

    # Step 1: Read document
    raw_document = read_document(DOCUMENT_PATH)

    # Step 2: Clean document
    document = clean_document(raw_document)

    # Step 3: Calculate deterministic metadata
    deterministic_metadata = calculate_metadata(
        document,
        DOCUMENT_PATH,
    )

    # Step 4: Extract semantic metadata using Ollama
    semantic_metadata = extract_semantic_metadata(document)

    # Step 5: Validate semantic metadata
    validate_semantic_metadata(semantic_metadata)

    # Step 6: Display metadata
    display_metadata(
        deterministic_metadata,
        semantic_metadata,
    )

    print("Exercise 69 completed successfully.")

    logger.info("Exercise 69 completed successfully")


if __name__ == "__main__":
    main()