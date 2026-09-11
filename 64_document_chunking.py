import logging
import json
from pathlib import Path


# ---------------------------------------------------------
# Logging configuration
# ---------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_document_chunker")


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------
DOCUMENT_PATH = Path("sample_document.txt")
OUTPUT_PATH = Path("document_chunks.json")

CHUNK_SIZE = 120
CHUNK_OVERLAP = 30


# ---------------------------------------------------------
# Read document
# ---------------------------------------------------------
def read_document(file_path: Path) -> str:
    """Read the document as text."""

    logger.info("Reading document: %s", file_path)

    if not file_path.exists():
        logger.error("Document not found: %s", file_path)
        raise FileNotFoundError(f"Document not found: {file_path}")

    text = file_path.read_text(encoding="utf-8")

    logger.info("Document read successfully")
    logger.info("Document characters: %d", len(text))

    return text


# ---------------------------------------------------------
# Clean document
# ---------------------------------------------------------
def clean_text(text: str) -> str:
    """Remove unnecessary whitespace."""

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
# Create chunks
# ---------------------------------------------------------
def create_chunks(
    text: str,
    chunk_size: int,
    chunk_overlap: int,
) -> list[dict]:
    """Split text into overlapping chunks."""

    logger.info(
        "Starting document chunking | chunk_size=%d | overlap=%d",
        chunk_size,
        chunk_overlap,
    )

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0")

    if chunk_overlap < 0:
        raise ValueError("chunk_overlap cannot be negative")

    if chunk_overlap >= chunk_size:
        raise ValueError("chunk_overlap must be smaller than chunk_size")

    chunks = []

    start = 0
    chunk_number = 1
    text_length = len(text)

    while start < text_length:
        end = min(start + chunk_size, text_length)

        chunk_text = text[start:end].strip()

        if chunk_text:
            chunk = {
                "chunk_id": chunk_number,
                "start": start,
                "end": end,
                "text": chunk_text,
                "characters": len(chunk_text),
                "words": len(chunk_text.split()),
            }

            chunks.append(chunk)

            logger.info(
                "Created chunk %d | characters=%d | words=%d",
                chunk_number,
                chunk["characters"],
                chunk["words"],
            )

            chunk_number += 1

        if end >= text_length:
            break

        # Move forward while keeping overlap
        start = end - chunk_overlap

    logger.info("Document chunking completed")
    logger.info("Total chunks created: %d", len(chunks))

    return chunks


# ---------------------------------------------------------
# Save chunks
# ---------------------------------------------------------
def save_chunks(chunks: list[dict], output_path: Path) -> None:
    """Save chunks as JSON."""

    logger.info("Saving chunks to: %s", output_path)

    output_path.write_text(
        json.dumps(chunks, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    logger.info("Chunks saved successfully")


# ---------------------------------------------------------
# Display chunks
# ---------------------------------------------------------
def display_chunks(chunks: list[dict]) -> None:
    """Display chunks in a readable format."""

    print("\n" + "=" * 60)
    print("DOCUMENT CHUNKS")
    print("=" * 60)

    for chunk in chunks:
        print(f"\nChunk {chunk['chunk_id']}")
        print("-" * 60)
        print(f"Start      : {chunk['start']}")
        print(f"End        : {chunk['end']}")
        print(f"Characters : {chunk['characters']}")
        print(f"Words      : {chunk['words']}")
        print(f"Text       : {chunk['text']}")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    logger.info("=" * 60)
    logger.info("Starting Exercise 64 - Document Chunking")
    logger.info("=" * 60)

    try:
        # Step 1: Read document
        raw_text = read_document(DOCUMENT_PATH)

        # Step 2: Clean document
        cleaned_text = clean_text(raw_text)

        # Step 3: Create chunks
        chunks = create_chunks(
            text=cleaned_text,
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
        )

        # Step 4: Save chunks
        save_chunks(chunks, OUTPUT_PATH)

        # Step 5: Display chunks
        display_chunks(chunks)

        print("\n" + "=" * 60)
        print("CHUNKING SUMMARY")
        print("=" * 60)
        print(f"Original characters : {len(raw_text)}")
        print(f"Cleaned characters  : {len(cleaned_text)}")
        print(f"Chunk size          : {CHUNK_SIZE}")
        print(f"Chunk overlap       : {CHUNK_OVERLAP}")
        print(f"Total chunks        : {len(chunks)}")
        print(f"Output file         : {OUTPUT_PATH}")

        print("\n" + "=" * 60)
        print("Exercise 64 completed successfully.")
        print("=" * 60)

        logger.info("Exercise 64 completed successfully")

    except Exception:
        logger.exception("Document chunking failed")
        raise


if __name__ == "__main__":
    main()