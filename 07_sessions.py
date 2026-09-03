from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.db.sqlite import SqliteDb


# -------------------------
# Create Agent
# -------------------------

agent = Agent(
    name="Session Assistant",
    model=Ollama(id="llama3.2"),
    db=SqliteDb(db_file="sessions.db"),

    # Add previous conversation history
    # to the context of the next message
    add_history_to_context=True,
    num_history_runs=5,
)


# -------------------------
# Session ID
# -------------------------

session_id = "avanthi-session-3"


# -------------------------
# First message
# -------------------------

agent.print_response(
    "My name is Avanthi. Remember my name.",
    session_id=session_id,
)


# -------------------------
# Second message
# -------------------------

agent.print_response(
    "What is my name?",
    session_id=session_id,
)