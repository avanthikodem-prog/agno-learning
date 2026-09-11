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

logger = logging.getLogger("gram_swaram_text_cleaner")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
DOCUMENT_PATH = Path("sample_document.txt")


# ---------------------------------------------------------
# Text extraction
# ---------------------------------------------------------
def extract_text(file_path: Path) -> str:
    """Extract raw text from a text document."""

    logger.info("Starting text extraction: %s", file_path)

    if not file_path.exists():
        logger.error("Document not found: %s", file_path)
        raise FileNotFoundError(f"Document not found: {file_path}")

    text = file_path.read_text(encoding="utf-8")

    logger.info("Text extraction completed")
    logger.info("Raw characters extracted: %d", len(text))

    return text


# ---------------------------------------------------------
# Text cleaning
# ---------------------------------------------------------
def clean_text(text: str) -> str:
    """Clean whitespace, blank lines, and spacing."""

    logger.info("Starting text cleaning")

    # Normalize Windows/Linux line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Remove unnecessary spaces at the beginning/end of lines
    lines = [line.strip() for line in text.split("\n")]

    # Remove empty lines
    lines = [line for line in lines if line]

    # Join lines back together
    cleaned_text = "\n".join(lines)

    # Replace multiple spaces with a single space
    cleaned_text = re.sub(r"[ \t]+", " ", cleaned_text)

    # Remove unnecessary spaces before punctuation
    cleaned_text = re.sub(r"\s+([,.!?;:])", r"\1", cleaned_text)

    logger.info("Text cleaning completed")
    logger.info("Cleaned characters: %d", len(cleaned_text))

    return cleaned_text


# ---------------------------------------------------------
# Text statistics
# ---------------------------------------------------------
def calculate_statistics(text: str) -> dict:
    """Calculate basic statistics for cleaned text."""

    logger.info("Calculating text statistics")

    words = text.split()
    sentences = re.split(r"[.!?]+", text)
    sentences = [sentence.strip() for sentence in sentences if sentence.strip()]
    lines = text.splitlines()

    statistics = {
        "characters": len(text),
        "words": len(words),
        "sentences": len(sentences),
        "lines": len(lines),
    }

    logger.info(
        "Statistics calculated: %d lines, %d sentences, %d words, %d characters",
        statistics["lines"],
        statistics["sentences"],
        statistics["words"],
        statistics["characters"],
    )

    return statistics


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    logger.info("=" * 60)
    logger.info("Starting Exercise 63 - Text Extraction & Cleaning")
    logger.info("=" * 60)

    try:
        # Step 1: Extract raw text
        raw_text = extract_text(DOCUMENT_PATH)

        # Step 2: Clean extracted text
        cleaned_text = clean_text(raw_text)

        # Step 3: Calculate statistics
        statistics = calculate_statistics(cleaned_text)

        # Step 4: Display result
        print("\n" + "=" * 60)
        print("TEXT EXTRACTION & CLEANING RESULT")
        print("=" * 60)

        print("\nCleaned Text:\n")
        print(cleaned_text)

        print("\nStatistics:")
        print(f"Lines      : {statistics['lines']}")
        print(f"Sentences  : {statistics['sentences']}")
        print(f"Words      : {statistics['words']}")
        print(f"Characters : {statistics['characters']}")

        print("\n" + "=" * 60)
        print("Exercise 63 completed successfully.")
        print("=" * 60)

        logger.info("Exercise 63 completed successfully")

    except Exception:
        logger.exception("Text extraction and cleaning failed")
        raise


if __name__ == "__main__":
    main()