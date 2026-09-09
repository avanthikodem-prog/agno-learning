import logging

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.db.sqlite import SqliteDb


# ============================================================
# LOGGER SETUP
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("gram_swaram_persistence")

logger.info("Starting persistent session test")


# ============================================================
# EXISTING DATABASE
# ============================================================

db = SqliteDb(
    db_file="gram_swaram_sessions.db"
)

logger.info("Connected to existing SQLite database")


# ============================================================
# AGNO AGENT
# ============================================================

agent = Agent(
    name="GramSwaram Persistent Session Agent",
    model=Ollama(id="llama3.2"),
    db=db,
    add_history_to_context=True,
    num_history_runs=5,
    instructions=[
        "You are a helpful GramSwaram assistant.",
        "Use previous conversation history when answering.",
        "Remember information from the user's session.",
        "Do not invent information.",
        "If you do not know something, say that you do not know.",
    ],
)

logger.info("Agno agent initialized")


# ============================================================
# SAME SESSION ID
# ============================================================

session_id = "farmer_ravi_001"

logger.info(
    "Opening existing session: %s",
    session_id
)


# ============================================================
# ASK ABOUT PREVIOUS INFORMATION
# ============================================================

message = """
What is my name and where am I from?
"""

print("=" * 60)
print("GRAMSWARAM PERSISTENT SESSION TEST")
print("=" * 60)

print("\nUser:")
print(message)

logger.info("Sending request using existing session")


try:

    response = agent.run(
        message,
        session_id=session_id,
    )

    print("\nAgent:")
    print(response.content)

    logger.info("Persistent session response generated successfully")

except Exception:

    logger.exception("Persistent session test failed")


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 60)
print("PERSISTENT SESSION TEST COMPLETE")
print("=" * 60)

logger.info("Persistent session test completed")