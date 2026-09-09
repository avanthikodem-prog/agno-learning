import logging
import os

from dotenv import load_dotenv
from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.db.postgres import PostgresDb


# --------------------------------------------------
# LOGGER
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_memory")

logger.info("Starting Agent Memory exercise")


# --------------------------------------------------
# LOAD ENVIRONMENT
# --------------------------------------------------

load_dotenv()

database_url = os.getenv("POSTGRES_DB_URL")

if not database_url:
    logger.error("POSTGRES_DB_URL was not found")
    raise ValueError("POSTGRES_DB_URL is missing from the .env file.")

logger.info("PostgreSQL database URL loaded successfully")


# --------------------------------------------------
# POSTGRESQL STORAGE
# --------------------------------------------------

db = PostgresDb(
    db_url=database_url
)

logger.info("PostgreSQL storage initialized")


# --------------------------------------------------
# AGENT
# --------------------------------------------------

agent = Agent(
    name="GramSwaram Memory Agent",

    model=Ollama(
        id="llama3.2"
    ),

    db=db,

    enable_agentic_memory=True,

    add_history_to_context=True,

    num_history_runs=5,

    instructions=[
        "You are a helpful GramSwaram farmer assistant.",
        "Remember useful information about the farmer.",
        "Use previous conversation information when appropriate.",
        "Do not invent farmer information.",
        "If you do not know something, say that you do not know.",
    ],
)

logger.info("Memory-enabled Agno agent initialized")


# --------------------------------------------------
# USER + SESSION
# --------------------------------------------------

user_id = "farmer_memory_002"

session_id = "memory_session_002"

logger.info("Using user ID: %s", user_id)

logger.info("Using session ID: %s", session_id)


# --------------------------------------------------
# FIRST MESSAGE
# --------------------------------------------------

message_1 = """
My name is Suresh.
I am a farmer from Nizamabad.
I grow turmeric.
"""

print("=" * 60)
print("GRAMSWARAM AGENT MEMORY")
print("=" * 60)

print("\nUser Message 1:")
print(message_1)

logger.info("Sending farmer information")


try:

    response_1 = agent.run(
        message_1,
        user_id=user_id,
        session_id=session_id,
    )

    print("\nAgent Response 1:")
    print(response_1.content)

    logger.info(
        "Farmer information processed successfully"
    )

except Exception:

    logger.exception(
        "Failed while processing farmer information"
    )

    raise


# --------------------------------------------------
# SECOND MESSAGE
# --------------------------------------------------

message_2 = """
What do you remember about me?
"""

print("\n" + "=" * 60)

print("\nUser Message 2:")
print(message_2)

logger.info(
    "Asking agent to recall farmer information"
)


try:

    response_2 = agent.run(
        message_2,
        user_id=user_id,
        session_id=session_id,
    )

    print("\nAgent Response 2:")
    print(response_2.content)

    logger.info(
        "Memory recall response generated successfully"
    )

except Exception:

    logger.exception(
        "Failed while recalling farmer information"
    )

    raise


# --------------------------------------------------
# COMPLETE
# --------------------------------------------------

print("\n" + "=" * 60)
print("AGENT MEMORY TEST COMPLETE")
print("=" * 60)

logger.info(
    "Agent Memory exercise completed successfully"
)