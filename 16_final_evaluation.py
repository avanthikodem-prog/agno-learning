from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.eval.accuracy import AccuracyEval


# 1. Create the Farmer Agent
farmer_agent = Agent(
    name="Farmer Evaluation Agent",
    model=Ollama(id="llama3.2"),
    instructions="""
    You are a helpful farmer assistant.

    Answer farming questions accurately,
    simply, and clearly.
    """,
)


# 2. Define evaluation questions
evaluations = [
    {
        "question": "What is the main benefit of drip irrigation?",
        "expected": (
            "Drip irrigation saves water by delivering "
            "water directly to the roots of plants."
        ),
    },
    {
        "question": "What crops does Ravi grow?",
        "expected": "Ravi grows paddy and cotton.",
    },
    {
        "question": "What is crop rotation?",
        "expected": (
            "Crop rotation means growing different crops "
            "in the same field in different seasons."
        ),
    },
]


# 3. Run each evaluation
scores = []

for i, item in enumerate(evaluations, start=1):

    print(f"\n========== EVALUATION {i} ==========\n")

    evaluation = AccuracyEval(
        name=f"Farmer Evaluation {i}",
        model=Ollama(id="llama3.2"),
        agent=farmer_agent,
        input=item["question"],
        expected_output=item["expected"],
        num_iterations=1,
    )

    result = evaluation.run(
        print_results=True
    )

    if result:
        score = result.avg_score
        scores.append(score)

        print(f"\nScore for Evaluation {i}: {score}/10")


# 4. Calculate overall score
if scores:

    average_score = sum(scores) / len(scores)

    print("\n========================================")
    print("       FINAL EVALUATION SUMMARY")
    print("========================================")

    print("Number of Evaluations:", len(scores))
    print("Scores:", scores)
    print(f"Average Score: {average_score:.2f}/10")