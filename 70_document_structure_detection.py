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

logger = logging.getLogger("gram_swaram_document_structure")


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

    logger.info(
        "Document loaded successfully: %d characters",
        len(text),
    )

    return text


# ---------------------------------------------------------
# Clean document
# ---------------------------------------------------------
def clean_document(text: str) -> str:
    """Normalize whitespace while preserving line structure."""

    logger.info("Cleaning document")

    cleaned_lines = []

    for line in text.splitlines():
        line = " ".join(line.split())

        if line:
            cleaned_lines.append(line)

    cleaned_text = "\n".join(cleaned_lines)

    logger.info(
        "Document cleaning completed: %d characters",
        len(cleaned_text),
    )

    return cleaned_text


# ---------------------------------------------------------
# Detect basic structure using Python
# ---------------------------------------------------------
def detect_basic_structure(document: str) -> dict:
    """Detect basic document structure deterministically."""

    logger.info("Detecting basic document structure")

    lines = document.splitlines()

    headings = []
    paragraphs = []
    lists = []

    for line in lines:

        # Detect numbered or bullet lists
        if re.match(r"^(\d+[\.\)]|[-*•])\s+", line):
            lists.append(line)

        # Detect simple heading-like lines
        elif (
            line.isupper()
            or line.endswith(":")
            or len(line.split()) <= 8
        ):
            headings.append(line)

        else:
            paragraphs.append(line)

    structure = {
        "total_lines": len(lines),
        "heading_count": len(headings),
        "paragraph_count": len(paragraphs),
        "list_item_count": len(lists),
        "headings": headings,
        "paragraphs": paragraphs,
        "lists": lists,
    }

    logger.info(
        "Structure detected: %d headings, %d paragraphs, %d list items",
        structure["heading_count"],
        structure["paragraph_count"],
        structure["list_item_count"],
    )

    return structure


# ---------------------------------------------------------
# Semantic structure detection using Ollama
# ---------------------------------------------------------
def detect_semantic_structure(document: str) -> str:
    """Ask Ollama to identify the semantic structure."""

    logger.info(
        "Sending document to Ollama for semantic structure detection"
    )

    client = Client(host=OLLAMA_HOST)

    prompt = f"""
You are a document structure analysis assistant.

Analyze ONLY the document provided below.

Identify the document's logical structure.

Return exactly these sections:

DOCUMENT TITLE:
Give the most appropriate title.

DOCUMENT TYPE:
Choose exactly ONE:
- Report
- Article
- Product Description
- Business Document
- Technical Document
- Educational Document
- Other

MAIN SECTIONS:
List the major logical sections or topics.

PARAGRAPH SUMMARY:
Give one short description of what the paragraphs discuss.

LISTS PRESENT:
Answer Yes or No.
If Yes, briefly describe them.

OVERALL STRUCTURE:
Describe the document structure in one short paragraph.

IMPORTANT RULES:
1. Use only information present in the document.
2. Do not use outside knowledge.
3. Do not invent sections that are not supported by the document.
4. Keep the response concise.
5. Follow the exact section format.

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
        "Semantic structure detection completed: %d characters",
        len(result),
    )

    return result


# ---------------------------------------------------------
# Validate semantic structure
# ---------------------------------------------------------
def validate_semantic_structure(result: str) -> None:
    """Validate required semantic sections."""

    logger.info("Validating semantic structure")

    required_sections = [
        "DOCUMENT TITLE:",
        "DOCUMENT TYPE:",
        "MAIN SECTIONS:",
        "PARAGRAPH SUMMARY:",
        "LISTS PRESENT:",
        "OVERALL STRUCTURE:",
    ]

    missing_sections = [
        section
        for section in required_sections
        if section not in result.upper()
    ]

    if missing_sections:
        logger.warning(
            "Missing sections: %s",
            ", ".join(missing_sections),
        )
    else:
        logger.info(
            "All expected semantic structure sections are present"
        )


# ---------------------------------------------------------
# Display results
# ---------------------------------------------------------
def display_structure(
    basic_structure: dict,
    semantic_structure: str,
) -> None:
    """Display document structure analysis."""

    print("\n" + "=" * 70)
    print("DOCUMENT STRUCTURE")
    print("=" * 70)

    print("\nDeterministic Structure:")
    print(f"Total Lines       : {basic_structure['total_lines']}")
    print(f"Heading Count     : {basic_structure['heading_count']}")
    print(f"Paragraph Count   : {basic_structure['paragraph_count']}")
    print(f"List Item Count   : {basic_structure['list_item_count']}")

    print("\nDetected Headings:")
    if basic_structure["headings"]:
        for index, heading in enumerate(
            basic_structure["headings"],
            start=1,
        ):
            print(f"{index}. {heading}")
    else:
        print("None")

    print("\nDetected Paragraphs:")
    if basic_structure["paragraphs"]:
        for index, paragraph in enumerate(
            basic_structure["paragraphs"],
            start=1,
        ):
            print(f"{index}. {paragraph}")
    else:
        print("None")

    print("\nDetected Lists:")
    if basic_structure["lists"]:
        for index, item in enumerate(
            basic_structure["lists"],
            start=1,
        ):
            print(f"{index}. {item}")
    else:
        print("None")

    print("\nSemantic Structure:")
    print(semantic_structure)

    print("\n" + "=" * 70)


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    logger.info(
        "Starting Exercise 70 - Document Structure Detection"
    )

    # Step 1: Read document
    raw_document = read_document(DOCUMENT_PATH)

    # Step 2: Clean document
    document = clean_document(raw_document)

    # Step 3: Detect basic structure using Python
    basic_structure = detect_basic_structure(document)

    # Step 4: Detect semantic structure using Ollama
    semantic_structure = detect_semantic_structure(document)

    # Step 5: Validate semantic structure
    validate_semantic_structure(semantic_structure)

    # Step 6: Display results
    display_structure(
        basic_structure,
        semantic_structure,
    )

    print("Exercise 70 completed successfully.")

    logger.info("Exercise 70 completed successfully")


if __name__ == "__main__":
    main()