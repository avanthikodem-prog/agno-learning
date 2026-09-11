import logging
from pathlib import Path


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_document_processor")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
DOCUMENT_PATH = Path("sample_document.txt")


# ---------------------------------------------------------
# Document processing functions
# ---------------------------------------------------------
def read_document(file_path: Path) -> str:
    """Read text from a document."""

    logger.info("Reading document: %s", file_path)

    if not file_path.exists():
        logger.error("Document not found: %s", file_path)
        raise FileNotFoundError(f"Document not found: {file_path}")

    text = file_path.read_text(encoding="utf-8")

    logger.info("Document successfully read")
    logger.info("Characters extracted: %d", len(text))

    return text


def clean_document(text: str) -> str:
    """Clean unnecessary whitespace from document text."""

    logger.info("Cleaning document text")

    cleaned_text = "\n".join(
        line.strip()
        for line in text.splitlines()
        if line.strip()
    )

    logger.info("Document cleaning completed")
    logger.info("Cleaned characters: %d", len(cleaned_text))

    return cleaned_text


def analyze_document(text: str) -> dict:
    """Generate basic document statistics."""

    logger.info("Analyzing document")

    words = text.split()
    lines = text.splitlines()

    result = {
        "characters": len(text),
        "words": len(words),
        "lines": len(lines),
    }

    logger.info("Document analysis completed")
    logger.info("Lines: %d", result["lines"])
    logger.info("Words: %d", result["words"])
    logger.info("Characters: %d", result["characters"])

    return result


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    logger.info("=" * 60)
    logger.info("Starting Exercise 62 - Basic Document Processing")
    logger.info("=" * 60)

    try:
        # Step 1: Read
        raw_text = read_document(DOCUMENT_PATH)

        # Step 2: Clean
        cleaned_text = clean_document(raw_text)

        # Step 3: Analyze
        statistics = analyze_document(cleaned_text)

        # Step 4: Display result
        print("\n" + "=" * 60)
        print("DOCUMENT PROCESSING RESULT")
        print("=" * 60)

        print("\nCleaned Document:\n")
        print(cleaned_text)

        print("\nDocument Statistics:")
        print(f"Lines      : {statistics['lines']}")
        print(f"Words      : {statistics['words']}")
        print(f"Characters : {statistics['characters']}")

        print("\n" + "=" * 60)
        print("Exercise 62 completed successfully.")
        print("=" * 60)

        logger.info("Exercise 62 completed successfully")

    except Exception:
        logger.exception("Document processing failed")
        raise


if __name__ == "__main__":
    main()