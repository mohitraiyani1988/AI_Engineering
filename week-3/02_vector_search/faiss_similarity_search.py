from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


# 1. Documents
documents = [
    "Sensor battery should be replaced every 12 months.",
    "Sensor connection can be established using Bluetooth.",
    "Battery level below 20 percent generates a warning.",
    "Temperature sensors operate between -20°C and 60°C.",
]


# 2. Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")


# 3. Generate document embeddings
document_embeddings = model.encode(documents)

print("Embedding shape:", document_embeddings.shape)


# 4. Create FAISS index
dimension = document_embeddings.shape[1]

index = faiss.IndexFlatL2(dimension)

index.add(
    np.array(document_embeddings).astype("float32")
)


# 5. User query
query = "When should I replace the sensor battery?"


# 6. Generate query embedding
query_embedding = model.encode([query])

query_embedding = np.array(query_embedding).astype("float32")


# 7. Search
top_k = 2

distances, indices = index.search(query_embedding, top_k)


# 8. Display results
print("\nQuery:")
print(query)

print("\nTop results:")

for rank, (distance, index_id) in enumerate(
    zip(distances[0], indices[0]),
    start=1
):
    print(f"\nRank {rank}")
    print(f"Distance: {distance:.4f}")
    print(f"Document: {documents[index_id]}")