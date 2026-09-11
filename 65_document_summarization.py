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

logger = logging.getLogger("gram_swaram_document_summarizer")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
DOCUMENT_PATH = Path("sample_document.txt")

OLLAMA_HOST = "http://127.0.0.1:11434"
MODEL_NAME = "llama3.2"

MAX_DOCUMENT_CHARACTERS = 4000


# ---------------------------------------------------------
# Ollama client
# ---------------------------------------------------------
client = Client(host=OLLAMA_HOST)


# ---------------------------------------------------------
# Read document
# ---------------------------------------------------------
def read_document(file_path: Path) -> str:
    """Read the document from disk."""

    logger.info("Reading document: %s", file_path)

    if not file_path.exists():
        logger.error("Document not found: %s", file_path)
        raise FileNotFoundError(f"Document not found: {file_path}")

    text = file_path.read_text(encoding="utf-8")

    logger.info("Document read successfully")
    logger.info("Characters read: %d", len(text))

    return text


# ---------------------------------------------------------
# Clean text
# ---------------------------------------------------------
def clean_text(text: str) -> str:
    """Clean unnecessary whitespace."""

    logger.info("Cleaning document text")

    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    cleaned_text = "\n".join(lines)

    logger.info("Text cleaning completed")
    logger.info("Cleaned characters: %d", len(cleaned_text))

    return cleaned_text


# ---------------------------------------------------------
# Generate summary
# ---------------------------------------------------------
def summarize_document(text: str) -> str:
    """Generate a summary using the local Ollama model."""

    logger.info("Starting document summarization")
    logger.info("Using Ollama host: %s", OLLAMA_HOST)
    logger.info("Using model: %s", MODEL_NAME)

    if len(text) > MAX_DOCUMENT_CHARACTERS:
        logger.warning(
            "Document exceeds maximum size of %d characters. Truncating.",
            MAX_DOCUMENT_CHARACTERS,
        )
        text = text[:MAX_DOCUMENT_CHARACTERS]

    prompt = f"""
You are a document summarization assistant.

Summarize the following document accurately.

Rules:
1. Use only information present in the document.
2. Do not invent facts.
3. Keep the summary concise.
4. Mention the main purpose of the document.
5. Mention the main capabilities or important points.
6. Return a clear paragraph followed by 3 key points.

DOCUMENT:
{text}
"""

    logger.info("Sending document to Ollama")

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

    summary = response["message"]["content"].strip()

    logger.info("Summary generated successfully")
    logger.info("Summary characters: %d", len(summary))

    return summary


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    logger.info("=" * 60)
    logger.info("Starting Exercise 65 - Document Summarization")
    logger.info("=" * 60)

    try:
        # Step 1: Read document
        raw_text = read_document(DOCUMENT_PATH)

        # Step 2: Clean document
        cleaned_text = clean_text(raw_text)

        # Step 3: Summarize using Ollama
        summary = summarize_document(cleaned_text)

        # Step 4: Display result
        print("\n" + "=" * 60)
        print("DOCUMENT SUMMARY")
        print("=" * 60)

        print("\n" + summary)

        print("\n" + "=" * 60)
        print("DOCUMENT PROCESSING PIPELINE")
        print("=" * 60)

        print("1. Document read")
        print("2. Text cleaned")
        print("3. Text sent to Ollama")
        print("4. Summary generated")

        print("\n" + "=" * 60)
        print("Exercise 65 completed successfully.")
        print("=" * 60)

        logger.info("Exercise 65 completed successfully")

    except Exception:
        logger.exception("Document summarization failed")
        raise


if __name__ == "__main__":
    main()