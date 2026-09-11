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

logger = logging.getLogger("gram_swaram_document_qa")


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
    """Read the source document from disk."""

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
    """Clean unnecessary whitespace from the document."""

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
# Ask question using Ollama
# ---------------------------------------------------------
def ask_question(document: str, question: str) -> str:
    """Ask Ollama a question using only the supplied document."""

    logger.info("Sending document question to Ollama")
    logger.info("Question: %s", question)

    client = Client(host=OLLAMA_HOST)

    prompt = f"""
You are a document question-answering assistant.

Answer the user's question using ONLY the information contained
in the document below.

IMPORTANT RULES:
1. Do not use outside knowledge.
2. Do not invent information.
3. Do not make assumptions.
4. If the answer is not present in the document, say:
   "The answer is not available in the document."
5. Keep the answer concise and clear.

DOCUMENT:
----------------
{document}
----------------

USER QUESTION:
{question}

ANSWER:
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

    answer = response["message"]["content"].strip()

    logger.info("Received answer from Ollama")
    logger.info("Answer length: %d characters", len(answer))

    return answer


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
def main() -> None:
    logger.info("Starting Exercise 66 - Document Q&A")

    # Step 1: Read document
    raw_document = read_document(DOCUMENT_PATH)

    # Step 2: Clean document
    document = clean_document(raw_document)

    # Step 3: Example question
    question = "Who is the CEO of GramSwaram?"

    # Step 4: Ask Ollama
    answer = ask_question(document, question)

    # Step 5: Display result
    print("\n" + "=" * 60)
    print("DOCUMENT Q&A")
    print("=" * 60)

    print(f"\nQuestion:\n{question}")

    print(f"\nAnswer:\n{answer}")

    print("\n" + "=" * 60)
    print("Exercise 66 completed successfully.")
    print("=" * 60)

    logger.info("Exercise 66 completed successfully")


if __name__ == "__main__":
    main()