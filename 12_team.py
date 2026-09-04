from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.team.team import Team


# Farmer Agent
farmer_agent = Agent(
    name="Farmer Agent",
    model=Ollama(id="llama3.2"),
    instructions="""
    You are a farmer information specialist.

    Answer questions about:
    - farmers
    - crops
    - farming practices
    - agriculture

    Give a clear and simple answer.
    """,
)


# Calculator Agent
calculator_agent = Agent(
    name="Calculator Agent",
    model=Ollama(id="llama3.2"),
    instructions="""
    You are a calculation specialist.

    Perform mathematical calculations accurately.
    Always provide the final numerical answer.
    """,
)


# Team
team = Team(
    name="Agriculture Team",
    model=Ollama(id="llama3.2"),
    members=[
        farmer_agent,
        calculator_agent,
    ],
    instructions="""
    You are the team leader.

    Delegate agriculture and farming questions to the Farmer Agent.
    Delegate mathematical questions to the Calculator Agent.

    After receiving the member's result, give the user a clear final answer.
    Do not return the delegation tool call as the final answer.
    """,
)


# Test
team.print_response(
     "What is 125 * 48 + 350?"
)