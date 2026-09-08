import os

from dotenv import load_dotenv
from agno.agent import Agent
from agno.db.postgres import PostgresDb
from agno.models.ollama import Ollama


# ============================================================
# 1. LOAD ENVIRONMENT
# ============================================================

load_dotenv()

db_url = os.getenv("POSTGRES_DB_URL")

if not db_url:
    raise ValueError("POSTGRES_DB_URL not found in .env")


# ============================================================
# 2. POSTGRESQL DATABASE
# ============================================================

db = PostgresDb(
    db_url=db_url,
    db_schema="ai",
)


# ============================================================
# 3. MEMORY AGENT
# ============================================================

agent = Agent(
    name="GramSwaram PostgreSQL Memory Agent",

    model=Ollama(
        id="llama3.2"
    ),

    db=db,

    update_memory_on_run=True,

    instructions="""
    You are a memory assistant.

    Remember useful information about the user.

    Use stored memories when answering future questions.

    Do not invent information.
    """,
)


# ============================================================
# 4. USER
# ============================================================

user_id = "platform-user"


# ============================================================
# 5. FIRST CONVERSATION
# ============================================================

print("\n" + "=" * 60)
print("CONVERSATION 1")
print("=" * 60)

agent.print_response(
    "My name is Ravi. I am a farmer and I grow paddy and cotton.",
    user_id=user_id,
    session_id="postgres-memory-test-1",
)


# ============================================================
# 6. SHOW STORED MEMORIES
# ============================================================

print("\n" + "=" * 60)
print("STORED MEMORIES")
print("=" * 60)

memories = agent.get_user_memories(
    user_id=user_id
)

for memory in memories:
    print("Memory:", memory.memory)


# ============================================================
# 7. SECOND CONVERSATION
# ============================================================

print("\n" + "=" * 60)
print("CONVERSATION 2")
print("=" * 60)

agent.print_response(
    "What is my name and what crops do I grow?",
    user_id=user_id,
    session_id="postgres-memory-test-2",
)