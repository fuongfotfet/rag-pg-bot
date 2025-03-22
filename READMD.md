# RAG PostgreSQL Bot

A Retrieval-Augmented Generation (RAG) bot that uses Elasticsearch and Ollama for document search and question answering.

## Components

- **Elasticsearch**: Vector database for storing and searching document embeddings
- **Ollama**: Local LLM for generating embeddings (using bge-m3) and text generation (using llama3.2)
- **Sentence Transformers**: For cross-encoding and relevance scoring

## Setup Requirements

1. Elasticsearch running on `http://localhost:9200`
2. Ollama with the following models:
   - bge-m3 (for embeddings)
   - llama3.2:1b (for text generation)
3. Python packages:
   ```
   elasticsearch
   ollama
   sentence-transformers
   numpy
   ```

## Main Features

### Vector Search
- Uses cosine similarity for semantic search
- Generates embeddings using bge-m3 model
- Returns top-k most relevant documents

### Answer Generation
- Retrieves relevant documents using vector search
- Constructs a prompt with context from retrieved documents
- Generates human-friendly answers using llama3.2

## Usage Example

```python
from services.text_qa import generate_answer

question = "Việc chuyển dữ liệu cá nhân ra nước ngoài"
answer = generate_answer(question, k=3, index_name='text_embeddings')
print(answer)
```

## Configuration

- Default vector search returns top 3 documents
- Uses 'text_embeddings' as default Elasticsearch index
- Embeddings are generated using the bge-m3 model
- Text generation uses llama3.2:1b model

