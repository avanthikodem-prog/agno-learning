from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.knowledge.knowledge import Knowledge
from agno.vectordb.chroma import ChromaDb
from agno.knowledge.embedder.ollama import OllamaEmbedder


# 1. Create ChromaDB
vector_db = ChromaDb(
    collection="farmer_knowledge",
    path="tmp/chromadb",
    persistent_client=True,
    embedder=OllamaEmbedder(
        id="nomic-embed-text",
        dimensions=768,
    ),
)


# 2. Create Knowledge
knowledge = Knowledge(
    name="Farmer Knowledge",
    description="Knowledge about farmers, crops and farming practices.",
    vector_db=vector_db,
)


# 3. Add farmer information
knowledge.insert(
    name="Ravi Farmer Information",
    text_content="""
    Ravi is a farmer from Telangana.
    He grows paddy and cotton.
    His farm uses drip irrigation.
    He has been farming for 10 years.
    """,
)

knowledge.insert(
    name="Suresh Farmer Information",
    text_content="""
    Suresh is a farmer from Andhra Pradesh.
    He grows rice and chilli.
    His farm uses traditional irrigation methods.
    He has been farming for 15 years.
    """,
)


# 4. Create Agent
agent = Agent(
    name="Farmer Knowledge Agent",
    model=Ollama(id="llama3.2"),
    knowledge=knowledge,
    search_knowledge=True,
    add_knowledge_to_context=True,
    instructions="""
    You are a farmer information assistant.

    Answer questions using the provided farmer knowledge.

    If the information is not available in the knowledge,
    clearly say that the information is not available.

    Do not invent information.
    """,
)


# 5. Ask questions
print("\n========== QUESTION 1 ==========\n")
agent.print_response("What crops does Ravi grow?")

print("\n========== QUESTION 2 ==========\n")
agent.print_response("How long has Ravi been farming?")

print("\n========== QUESTION 3 ==========\n")
agent.print_response("What crops does Suresh grow?")

print("\n========== QUESTION 4 ==========\n")
agent.print_response("What crops does Ramesh grow?")