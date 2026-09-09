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

logger = logging.getLogger("gram_swaram_sessions")

logger.info("Starting GramSwaram Session Agent")


# ============================================================
# DATABASE
# ============================================================

db = SqliteDb(
    db_file="gram_swaram_sessions.db"
)

logger.info("SQLite database initialized")


# ============================================================
# AGNO AGENT
# ============================================================

agent = Agent(
    name="GramSwaram Session Agent",
    model=Ollama(id="llama3.2"),
    db=db,

    # Important:
    # Include previous conversation history in the model context.
    add_history_to_context=True,

    # Number of previous runs to include.
    num_history_runs=5,

    instructions=[
        "You are a helpful GramSwaram assistant.",
        "Remember information provided by the user during the session.",
        "Use previous conversation context when answering.",
        "Do not invent information.",
        "If you do not know something, clearly say that you do not know.",
    ],
)

logger.info("Agno agent initialized")


# ============================================================
# SESSION
# ============================================================

session_id = "farmer_ravi_001"

logger.info("Using session ID: %s", session_id)


# ============================================================
# FIRST MESSAGE
# ============================================================

message_1 = """
My name is Ravi.
I am a farmer from Nizamabad.
"""

print("=" * 60)
print("GRAMSWARAM SESSION TEST")
print("=" * 60)

print("\nUser Message 1:")
print(message_1)

logger.info("Sending first message")

response_1 = agent.run(
    message_1,
    session_id=session_id,
)

print("\nAgent Response 1:")
print(response_1.content)

logger.info("First response generated successfully")


# ============================================================
# SECOND MESSAGE
# ============================================================

message_2 = """
What is my name and where am I from?
"""

print("\n" + "=" * 60)

print("\nUser Message 2:")
print(message_2)

logger.info("Sending second message")

response_2 = agent.run(
    message_2,
    session_id=session_id,
)

print("\nAgent Response 2:")
print(response_2.content)

logger.info("Second response generated successfully")


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 60)
print("SESSION TEST COMPLETE")
print("=" * 60)

logger.info("GramSwaram session test completed")