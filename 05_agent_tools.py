from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.tools.calculator import CalculatorTools


agent = Agent(
    name="Calculator Agent",
    model=Ollama(id="llama3.2"),
    tools=[CalculatorTools()],
    instructions="Use the calculator tool when mathematical calculations are required.",
)

agent.print_response(
    "What is 125 * 48 + 350?"
)
