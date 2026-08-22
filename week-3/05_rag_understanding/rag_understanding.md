# RAG — Retrieval-Augmented Generation

## 1. What is RAG?

Retrieval-Augmented Generation (RAG) is an architecture that allows an LLM
to answer questions using external knowledge retrieved at runtime.

Instead of putting all company documents directly into the LLM prompt,
documents are processed and stored in a searchable vector database.

When a user asks a question, relevant document chunks are retrieved and
provided to the LLM as context.

---

## 2. RAG Architecture

![RAG Pipeline](./rag_pipeline.png)

---

## 3. Document Ingestion Flow

Documents are processed before users ask questions.

Document
→ Text Extraction
→ Cleaning
→ Chunking
→ Embedding
→ Vector Database

Document embeddings are generated during ingestion and normally do not
need to be regenerated unless the document or embedding model changes.

---

## 4. Query Flow

When the user asks a question:

User Query
→ Query Embedding
→ Vector Similarity Search
→ Top-K Relevant Chunks
→ Prompt Augmentation
→ LLM
→ Final Response

The query embedding is generated for every new query because each user
question can have different semantic meaning.

---

## 5. Main Components

### Document Loader / Text Extraction
Extracts text from PDFs, DOCX, HTML, etc.

### Chunking
Breaks large documents into smaller pieces that can be independently
retrieved.

### Embedding Model
Converts text into numerical vectors representing semantic meaning.

### Vector Database
Stores embeddings and allows similarity search.

Examples:
- FAISS
- Chroma
- Qdrant
- Pinecone

### Retriever
Finds the most relevant chunks for a user query.

### LLM
Uses the retrieved context and user question to generate the final answer.

---

## 6. Why RAG?

RAG allows applications to use information that was not part of the
LLM's original training data.

It is particularly useful for:

- Frequently changing company documentation
- Internal policies
- Product documentation
- Technical documentation
- Knowledge bases

When a document changes, the affected document chunks and embeddings can
be updated without retraining the LLM.

---

## 7. RAG vs Fine-Tuning

| RAG | Fine-Tuning |
|---|---|
| Adds external knowledge at runtime | Changes model behavior/weights |
| Good for frequently changing information | Useful for behavior/style/task specialization |
| Documents can be updated independently | Updating knowledge generally requires another training process |
| Retrieves relevant information | Does not perform document retrieval by itself |
| Knowledge remains outside the model | Learned information becomes part of model parameters |

---

## 8. Example

Suppose HR updates a leave policy.

The application:

1. Extracts the updated document.
2. Cleans and chunks the text.
3. Generates embeddings.
4. Updates the corresponding records in the vector database.

The LLM itself does not need to be retrained.

When an employee asks:

"How many days of parental leave can I take?"

the application:

1. Creates an embedding for the question.
2. Searches the vector database.
3. Retrieves the relevant policy chunks.
4. Adds those chunks to the prompt.
5. Sends the augmented prompt to the LLM.
6. Returns the generated answer.

---

## 9. Important RAG Failure Points

RAG does not automatically guarantee correct answers.

Potential failures include:

- Poor document extraction
- Poor chunking
- Incorrect embeddings
- Poor retrieval
- Incorrect Top-K
- Missing relevant chunks
- Too much irrelevant context
- LLM misunderstanding the retrieved context
- LLM hallucination

Therefore:

> Retrieval quality is one of the most important factors in overall RAG quality.

---

## 10. Summary

RAG separates knowledge retrieval from language generation.

Document knowledge is stored externally in a searchable representation,
while the LLM is responsible for understanding the retrieved context and
generating the response.


                    RAG ARCHITECTURE

 DOCUMENT INGESTION                         USER QUERY
 ───────────────────                       ──────────

 PDF / DOC / HTML                           User Question
       │                                          │
       ▼                                          ▼
 Text Extraction                           Query Embedding
       │                                          │
       ▼                                          │
 Cleaning                                          │
       │                                          │
       ▼                                          │
 Chunking                                          │
       │                                          │
       ▼                                          │
 Embedding Model                                   │
       │                                          │
       ▼                                          ▼
 ┌────────────────────────────────────────────────────┐
 │                 VECTOR DATABASE                    │
 │                                                    │
 │  Embeddings + Chunks + Metadata                    │
 └──────────────────────┬─────────────────────────────┘
                        │
                        │ Similarity Search
                        ▼
                  Top-K Chunks
                        │
                        ▼
              Prompt + Retrieved Context
                        │
                        ▼
                       LLM
                        │
                        ▼
                  Final Response