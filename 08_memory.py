from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.db.sqlite import SqliteDb


# --------------------------------------------------
# 1. Database for persistent memory
# --------------------------------------------------

db = SqliteDb(
    db_file="memory.db"
)


# --------------------------------------------------
# 2. Create Agent
# --------------------------------------------------

agent = Agent(
    name="Memory Assistant",
    model=Ollama(id="llama3.2"),
    db=db,

    # Store user memories automatically
    update_memory_on_run=True,

    # Add stored memories to the Agent's context
    add_memories_to_context=True,
)


# --------------------------------------------------
# 3. User ID
# --------------------------------------------------

user_id = "avanthi"


# --------------------------------------------------
# 4. First conversation
#    Store information about the user
# --------------------------------------------------

print("\n========== FIRST CONVERSATION ==========\n")

agent.print_response(
    "My name is Avanthi. I am learning AI agents and I am interested in machine learning.",
    user_id=user_id,
    session_id="memory-session-1",
)


# --------------------------------------------------
# 5. Check what was stored in memory
# --------------------------------------------------

print("\n========== STORED MEMORIES ==========\n")

memories = agent.get_user_memories(
    user_id=user_id
)

for memory in memories:
    print("Memory:", memory.memory)


# --------------------------------------------------
# 6. New conversation
#    Ask the Agent about the stored memory
# --------------------------------------------------

print("\n========== SECOND CONVERSATION ==========\n")

agent.print_response(
    "What is my name and what am I learning? Use the information you remember about me.",
    user_id=user_id,
    session_id="memory-session-2",
)
