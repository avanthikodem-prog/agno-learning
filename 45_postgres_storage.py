import logging
import os

from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.db.postgres import PostgresDb


# ============================================================
# LOGGER SETUP
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_postgres")

logger.info("Starting PostgreSQL storage exercise")


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

database_url = os.getenv("POSTGRES_DB_URL")

if not database_url:
    logger.error("POSTGRES_DB_URL was not found")

    raise ValueError(
        "POSTGRES_DB_URL is missing from the .env file."
    )

logger.info("PostgreSQL database URL loaded successfully")


# ============================================================
# POSTGRESQL STORAGE
# ============================================================

db = PostgresDb(
    db_url=database_url
)

logger.info("PostgreSQL storage initialized")


# ============================================================
# AGNO AGENT
# ============================================================

agent = Agent(
    name="GramSwaram PostgreSQL Agent",
    model=Ollama(id="llama3.2"),
    db=db,

    add_history_to_context=True,
    num_history_runs=5,

    instructions=[
        "You are a helpful GramSwaram assistant.",
        "Use previous conversation history when answering.",
        "Remember information provided during the session.",
        "Do not invent information.",
        "If you do not know something, clearly say that you do not know.",
    ],
)

logger.info("Agno agent initialized")


# ============================================================
# SESSION
# ============================================================

session_id = "farmer_postgres_001"

logger.info(
    "Using PostgreSQL session ID: %s",
    session_id
)


# ============================================================
# FIRST MESSAGE
# ============================================================

message_1 = """
My name is Ramesh.
I am a farmer from Nizamabad.
I grow turmeric.
"""

print("=" * 60)
print("GRAMSWARAM POSTGRESQL STORAGE")
print("=" * 60)

print("\nUser Message 1:")
print(message_1)

logger.info("Sending first message")

try:

    response_1 = agent.run(
        message_1,
        session_id=session_id,
    )

    print("\nAgent Response 1:")
    print(response_1.content)

    logger.info("First response generated and stored")

except Exception:

    logger.exception(
        "Failed while processing first message"
    )

    raise


# ============================================================
# SECOND MESSAGE
# ============================================================

message_2 = """
What crop do I grow?
"""

print("\n" + "=" * 60)

print("\nUser Message 2:")
print(message_2)

logger.info("Sending second message")

try:

    response_2 = agent.run(
        message_2,
        session_id=session_id,
    )

    print("\nAgent Response 2:")
    print(response_2.content)

    logger.info("Second response generated successfully")

except Exception:

    logger.exception(
        "Failed while processing second message"
    )

    raise


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 60)
print("POSTGRESQL STORAGE TEST COMPLETE")
print("=" * 60)

logger.info(
    "PostgreSQL storage exercise completed successfully"
)