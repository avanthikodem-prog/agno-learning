from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.eval.accuracy import AccuracyEval


# 1. Create our Farmer Agent
farmer_agent = Agent(
    name="Farmer Evaluation Agent",
    model=Ollama(id="llama3.2"),
    instructions="""
    You are a helpful farmer assistant.

    Answer farming questions accurately,
    simply, and clearly.
    """,
)


# 2. Create the evaluation
evaluation = AccuracyEval(
    name="Drip Irrigation Evaluation",

    # Model used as the evaluator / judge
    model=Ollama(id="llama3.2"),

    # Agent we want to test
    agent=farmer_agent,

    # Question given to the agent
    input="What is the main benefit of drip irrigation?",

    # Ideal answer
    expected_output=(
        "Drip irrigation saves water by delivering water "
        "directly to the roots of plants."
    ),

    # Run once for now
    num_iterations=1,
)


# 3. Run the evaluation
if __name__ == "__main__":

    result = evaluation.run(
        print_results=True
    )

    print("\n========== EVALUATION RESULT ==========\n")

    if result:
        print("Average Score:", result.avg_score)