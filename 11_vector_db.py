import chromadb


# Create a persistent ChromaDB client
client = chromadb.PersistentClient(
    path="tmp/vector_db"
)


# Create a collection
collection = client.get_or_create_collection(
    name="farmer_data"
)


# Add documents
collection.add(
    ids=["farmer_1", "farmer_2"],
    documents=[
        "Ravi is a farmer from Telangana. He grows paddy and cotton.",
        "Suresh is a farmer from Andhra Pradesh. He grows rice and chilli.",
    ],
)


print("Documents added successfully!")

print("\nTotal documents:", collection.count())


# Search for similar documents
results = collection.query(
    query_texts=[
        "What crops does the Andhra Pradesh farmer grow?"
    ],
    n_results=2,
)

print("\n========== SEARCH RESULTS ==========\n")

print("Documents:")
print(results["documents"])

print("\nDistances:")
print(results["distances"])