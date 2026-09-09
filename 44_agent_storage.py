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

logger = logging.getLogger("gram_swaram_storage")

logger.info("Starting Agent Storage exercise")


# ============================================================
# STORAGE
# ============================================================

db = SqliteDb(
    db_file="gram_swaram_agent_storage.db"
)

logger.info("SQLite storage initialized")


# ============================================================
# AGENT
# ============================================================

agent = Agent(
    name="GramSwaram Storage Agent",
    model=Ollama(id="llama3.2"),
    db=db,

    add_history_to_context=True,
    num_history_runs=5,

    instructions=[
        "You are a helpful GramSwaram assistant.",
        "Use the conversation history when answering.",
        "Remember information provided during the session.",
        "Do not invent information.",
        "If you do not know something, say that you do not know.",
    ],
)

logger.info("Agno agent initialized")


# ============================================================
# SESSION
# ============================================================

session_id = "farmer_sita_001"

logger.info("Using session ID: %s", session_id)


# ============================================================
# FIRST CONVERSATION
# ============================================================

message_1 = """
My name is Sita.
I am a farmer from Nizamabad.
I grow rice.
"""

print("=" * 60)
print("GRAMSWARAM AGENT STORAGE")
print("=" * 60)

print("\nUser Message 1:")
print(message_1)

logger.info("Sending first conversation message")

response_1 = agent.run(
    message_1,
    session_id=session_id,
)

print("\nAgent Response 1:")
print(response_1.content)

logger.info("First response stored successfully")


# ============================================================
# SECOND CONVERSATION
# ============================================================

message_2 = """
What crop do I grow?
"""

print("\n" + "=" * 60)

print("\nUser Message 2:")
print(message_2)

logger.info("Sending second conversation message")

response_2 = agent.run(
    message_2,
    session_id=session_id,
)

print("\nAgent Response 2:")
print(response_2.content)

logger.info("Second response stored successfully")


# ============================================================
# COMPLETE
# ============================================================

print("\n" + "=" * 60)
print("AGENT STORAGE TEST COMPLETE")
print("=" * 60)

logger.info("Agent Storage exercise completed")