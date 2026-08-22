# What is an embedding?

An embedding is a numerical representation of meaning.

For example:

"How do I reset my sensor?"

is converted by an embedding model into something like:

[0.021, -0.382, 0.741, 0.119, ...]

The real vector may contain hundreds or thousands of numbers.

The important point is:

The numbers represent the semantic characteristics of the text.

Where does the embedding model come from?

It's a separate model designed specifically for embeddings.

For example, Google's ecosystem currently provides embedding models such as:

Gemini Embedding

There are also open-source embedding models such as:

BGE
E5
Sentence Transformers

You don't normally use your chat LLM itself to create your application's embeddings.

Your architecture can therefore be:

                 Chat
                  ↓
             Chat Model
                  ↓
               Answer




Documents → Embedding Model → Vector DB
                                ↑
Query → Embedding Model ─────────┘

Notice that the chat model and embedding model have different jobs.

# What is a vector database?

Suppose we have 4 documents:

D1 → Sensor battery should be replaced every 12 months.


D2 → Sensor connection can be established using Bluetooth.


D3 → Battery level below 20% generates a warning.


D4 → Temperature sensors operate between -20°C and 60°C.

We generate embeddings:

D1 → [0.12, -0.43, 0.87, ...]
D2 → [0.81,  0.22, -0.14, ...]
D3 → [0.15, -0.40, 0.82, ...]
D4 → [-0.33, 0.71, 0.12, ...]

The vector database stores something conceptually like:

┌────┬─────────────────────────────┬─────────────────────┐
│ ID │ Document                    │ Embedding           │
├────┼─────────────────────────────┼─────────────────────┤
│ D1 │ Battery replaced...         │ [0.12,-0.43,...]   │
│ D2 │ Bluetooth connection...     │ [0.81, 0.22,...]   │
│ D3 │ Battery warning...          │ [0.15,-0.40,...]   │
│ D4 │ Temperature range...        │ [-0.33,0.71,...]   │
└────┴─────────────────────────────┴─────────────────────┘

The database's job is to efficiently find vectors that are closest to the query vector.


# Now a user asks a question
"When should I replace the sensor battery?"

We embed the question:

Query
 ↓
Embedding Model
 ↓
[0.14, -0.41, 0.84, ...]

The vector database compares it with the stored vectors.

Conceptually:

Query
  │
  ├── D1 → similarity: 0.94 ⭐
  ├── D3 → similarity: 0.88
  ├── D2 → similarity: 0.31
  └── D4 → similarity: 0.18

So we retrieve:

D1
D3

depending on our top-k.

# Then RAG adds the LLM

RAG takes those retrieved documents and gives them to the LLM:

                 User Query
                     │
                     ▼
               Embedding Model
                     │
                     ▼
                Vector Search
                     │
                     ▼
                Top-K Chunks
                     │
                     ▼
          ┌─────────────────────┐
          │       Prompt        │
          │                     │
          │ Context:            │
          │ D1                  │
          │ D3                  │
          │                     │
          │ Question:           │
          │ When should I       │
          │ replace battery?    │
          └──────────┬──────────┘
                     │
                     ▼
                    LLM
                     │
                     ▼
                  Answer

That's Retrieval-Augmented Generation.

The word itself tells you what happens:

Retrieval → find relevant information.

Augmented → add that information to the prompt.

Generation → LLM generates the answer.

# One sentence to remember

Embedding converts meaning into numbers, Vector Search finds similar meanings, and RAG gives those results to an LLM so it can generate an answer.

# FAISS stands for Facebook AI Similarity Search. It is an open-source library from Meta AI for fast similarity search over vectors (embeddings).

Think of it as:

A search engine for embeddings.

# FAISS is a search library

What we just did:

Documents
   ↓
Embedding Model
   ↓
Vectors
   ↓
FAISS
   ↓
Similarity Search

FAISS is extremely good at one core job:

Find similar vectors quickly.

But a real RAG application needs more than that.

# A vector database adds the surrounding infrastructure

A vector database typically stores something conceptually like:

┌──────────┬────────────────────┬──────────────────────┐
│ ID       │ Embedding          │ Document / Metadata  │
├──────────┼────────────────────┼──────────────────────┤
│ sensor-1 │ [0.12,-0.43,...]   │ Battery policy       │
│ sensor-2 │ [0.81,0.22,...]    │ Bluetooth guide      │
│ sensor-3 │ [0.15,-0.40,...]   │ Battery warning      │
└──────────┴────────────────────┴──────────────────────┘

So when you search, you can get back:

Document
Embedding
Metadata
ID
Similarity score

rather than managing everything separately.


