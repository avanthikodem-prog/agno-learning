from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.workflow.workflow import Workflow
from agno.workflow.types import StepInput, StepOutput


# AI Agent
farmer_agent = Agent(
    name="Farmer Analysis Agent",
    model=Ollama(id="llama3.2"),
    instructions="""
    You are a farming analysis specialist.

    Analyze the farmer information provided to you.
    Give a simple and clear analysis.
    """,
)


def farmer_info_step(step_input: StepInput) -> StepOutput:
    """Step 1: Get farmer information."""

    return StepOutput(
        content=(
            "Ravi is a farmer from Telangana. "
            "He grows paddy and cotton."
        )
    )


def analysis_step(step_input: StepInput) -> StepOutput:
    """Step 2: Use AI agent to analyze the information."""

    farmer_info = step_input.previous_step_content

    response = farmer_agent.run(
        f"Analyze this farmer information:\n{farmer_info}"
    )

    return StepOutput(
        content=response.content
    )


workflow = Workflow(
    name="AI Farmer Workflow",
    steps=[
        farmer_info_step,
        analysis_step,
    ],
)


if __name__ == "__main__":
    workflow.print_response(
        input="Analyze Ravi's farming information."
    )