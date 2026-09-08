import os

import psycopg
from dotenv import load_dotenv

from agno.agent import Agent
from agno.models.ollama import Ollama


# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

db_url = os.getenv("POSTGRES_DB_URL")

if not db_url:
    raise ValueError(
        "POSTGRES_DB_URL not found in .env file."
    )


# ============================================================
# 2. CREATE POSTGRESQL MEMORY TABLE
# ============================================================

def create_memory_table():
    """
    Create the PostgreSQL table used for
    GramSwaram persistent user memory.
    """

    with psycopg.connect(db_url) as conn:

        with conn.cursor() as cur:

            # Make sure the ai schema exists
            cur.execute(
                """
                CREATE SCHEMA IF NOT EXISTS ai;
                """
            )

            # Create our own memory table
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS ai.gramswaram_user_memories (
                    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    memory TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW()
                );
                """
            )

        conn.commit()

    print("PostgreSQL memory table is ready.")


# ============================================================
# 3. SAVE MEMORY
# ============================================================

def save_user_memory(user_id: str, memory: str):
    """
    Save a memory for a user in PostgreSQL.
    """

    with psycopg.connect(db_url) as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                INSERT INTO ai.gramswaram_user_memories
                    (user_id, memory)
                VALUES
                    (%s, %s);
                """,
                (user_id, memory),
            )

        conn.commit()

    print(f"Memory saved for user: {user_id}")


# ============================================================
# 4. GET USER MEMORIES
# ============================================================

def get_user_memories(user_id: str) -> list[str]:
    """
    Retrieve all stored memories for a user.
    """

    with psycopg.connect(db_url) as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT memory
                FROM ai.gramswaram_user_memories
                WHERE user_id = %s
                ORDER BY created_at ASC;
                """,
                (user_id,),
            )

            rows = cur.fetchall()

    return [row[0] for row in rows]


# ============================================================
# 5. BUILD MEMORY CONTEXT
# ============================================================

def build_memory_context(user_id: str) -> str:
    """
    Convert PostgreSQL memories into context
    that can be given to the AI agent.
    """

    memories = get_user_memories(user_id)

    if not memories:
        return "No previous memory is available."

    return "\n".join(
        f"- {memory}"
        for memory in memories
    )


# ============================================================
# 6. CREATE MEMORY AGENT
# ============================================================

memory_agent = Agent(
    name="GramSwaram Memory Agent",
    model=Ollama(id="llama3.2"),

    instructions=[
        "You are the GramSwaram Memory Assistant.",

        "Use ONLY the memory context provided by the application.",

        "Do not invent information.",

        "If the answer is available in the memory context, "
        "answer directly.",

        "If the answer is not available in the memory context, "
        "say that the information is not available in memory.",

        "Do not use tools.",
    ],
)


# ============================================================
# 7. MAIN TEST
# ============================================================

if __name__ == "__main__":

    print("\n" + "=" * 60)
    print("GRAMSWARAM POSTGRESQL EXPLICIT MEMORY TEST")
    print("=" * 60)


    # --------------------------------------------------------
    # Create table
    # --------------------------------------------------------

    create_memory_table()


    # --------------------------------------------------------
    # User ID
    # --------------------------------------------------------

    user_id = "platform-user"


    # --------------------------------------------------------
    # CONVERSATION 1
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("CONVERSATION 1")
    print("=" * 60)

    first_message = (
        "My name is Ravi. "
        "I am a farmer and I grow paddy and cotton."
    )

    print("\nUser:")
    print(first_message)


    # Save useful information directly to PostgreSQL
    save_user_memory(
        user_id,
        "The user's name is Ravi."
    )

    save_user_memory(
        user_id,
        "The user is a farmer."
    )

    save_user_memory(
        user_id,
        "The user grows paddy and cotton."
    )


    print("\nMemory saved successfully.")


    # --------------------------------------------------------
    # SHOW STORED MEMORIES
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("MEMORIES STORED IN POSTGRESQL")
    print("=" * 60)

    memories = get_user_memories(user_id)

    for memory in memories:
        print("Memory:", memory)


    # --------------------------------------------------------
    # BUILD MEMORY CONTEXT
    # --------------------------------------------------------

    memory_context = build_memory_context(user_id)

    print("\n" + "=" * 60)
    print("MEMORY CONTEXT SENT TO AGENT")
    print("=" * 60)

    print(memory_context)


    # --------------------------------------------------------
    # CONVERSATION 2
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("CONVERSATION 2")
    print("=" * 60)

    second_message = (
        "What is my name and what crops do I grow?"
    )

    print("\nUser:")
    print(second_message)


    # Give PostgreSQL memory to the agent
    prompt = f"""
Memory from PostgreSQL:

{memory_context}

User question:

{second_message}

Answer the question using only the memory above.
"""


    print("\nAgent:")

    memory_agent.print_response(
        prompt
    )


    # --------------------------------------------------------
    # FINAL MESSAGE
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("POSTGRESQL EXPLICIT MEMORY TEST COMPLETED")
    print("=" * 60)
