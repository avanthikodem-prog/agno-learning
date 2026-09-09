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

logger = logging.getLogger("gram_swaram_state")

logger.info("Starting Agent State exercise")


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

database_url = os.getenv("POSTGRES_DB_URL")

if not database_url:
    logger.error("POSTGRES_DB_URL was not found")
    raise ValueError("POSTGRES_DB_URL is missing from the .env file.")

logger.info("PostgreSQL database URL loaded successfully")


# ============================================================
# POSTGRESQL STORAGE
# ============================================================

db = PostgresDb(
    db_url=database_url
)

logger.info("PostgreSQL storage initialized")


# ============================================================
# INITIAL SESSION STATE
# ============================================================

session_state = {
    "farmer_name": "Suresh",
    "location": "Nizamabad",
    "current_crop": "Turmeric",
    "irrigation_needed": True,
}

logger.info("Initial session state created")
logger.info("Current crop: %s", session_state["current_crop"])
logger.info(
    "Irrigation needed: %s",
    session_state["irrigation_needed"],
)


# ============================================================
# CREATE AGENT
# ============================================================

agent = Agent(
    name="GramSwaram State Agent",

    model=Ollama(
        id="llama3.2"
    ),

    db=db,

    session_state=session_state,

    add_session_state_to_context=True,

    add_history_to_context=True,

    num_history_runs=5,

    instructions=[
        "You are a helpful GramSwaram farmer assistant.",
        "Use the session state when answering questions.",
        "Do not invent farmer information.",
        "If information is not available, clearly say that you do not know.",
        "Keep responses concise and useful.",
    ],
)

logger.info("Agent with session state initialized")


# ============================================================
# USER AND SESSION
# ============================================================

user_id = "farmer_state_001"

session_id = "state_session_001"

logger.info("Using user ID: %s", user_id)

logger.info("Using session ID: %s", session_id)


# ============================================================
# FIRST REQUEST
# ============================================================

message_1 = """
Please remember my current farming information.

My name is Suresh.
I am from Nizamabad.
My current crop is turmeric.
I need irrigation for this crop.
"""

print("=" * 60)
print("GRAMSWARAM AGENT STATE")
print("=" * 60)

print("\nUser Message 1:")
print(message_1)

logger.info("Sending first request to the agent")


try:
    response_1 = agent.run(
        message_1,
        user_id=user_id,
        session_id=session_id,
    )

    print("\nAgent Response 1:")
    print(response_1.content)

    logger.info("First request processed successfully")

except Exception:
    logger.exception("First agent request failed")
    raise


# ============================================================
# SECOND REQUEST
# ============================================================

message_2 = """
What is my current crop, and does it need irrigation?
"""

print("\n" + "=" * 60)

print("\nUser Message 2:")
print(message_2)

logger.info("Testing session state retrieval")


try:
    response_2 = agent.run(
        message_2,
        user_id=user_id,
        session_id=session_id,
    )

    print("\nAgent Response 2:")
    print(response_2.content)

    logger.info("Session state retrieved successfully")

except Exception:
    logger.exception("Second agent request failed")
    raise


# ============================================================
# DISPLAY STATE
# ============================================================

print("\n" + "=" * 60)
print("SESSION STATE")
print("=" * 60)

print("\nFarmer Name:", session_state["farmer_name"])
print("Location:", session_state["location"])
print("Current Crop:", session_state["current_crop"])
print("Irrigation Needed:", session_state["irrigation_needed"])

logger.info("Session state displayed successfully")


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 60)
print("AGENT STATE TEST COMPLETE")
print("=" * 60)

logger.info("Agent State exercise completed successfully")