# RAG FeinGiang Bot

RAG bot using Elasticsearch and Ollama for document search and question answering.

## Prerequisites

- Docker and Docker Compose
- Python 3.8+ (for local development)

## Quick Start

### Using Docker Compose (Recommended)

You can choose to run `run.sh` on your Linux machine

```bash
sh ./run.sh
```

or If you're not using Linux, try `docker compose` instead

```bash
# Both platform Windows and Linux
docker compose build app
docker compose up -d
```

### Local Development
1. Set environment variables:
```bash
# Linux/Mac
export ELASTIC_HOST=localhost
export ELASTIC_PORT=9200

# Windows PowerShell
$env:ELASTIC_HOST="localhost"
$env:ELASTIC_PORT="9200"
```

2. Run setup script:
```bash
# Linux/Mac
./setup.sh

# Windows
.\setup.ps1
```

## Usage Example
```python
from services.text_qa import generate_answer

question = "Your question here"
answer = generate_answer(question)
print(answer)
```

## Components
- Elasticsearch: Vector database
- Ollama (bge-m3, llama3.2:1b): Embeddings and text generation
- Python packages: elasticsearch, ollama, sentence-transformers

## Project Structure

```
rag-pg-bot/
├── services/
│   └── text_qa.py  ..,    # Main QA service implementation
├── README.md
```

## Running the Project

1. Ensure Elasticsearch is running:
   ```bash
   docker ps  # Should show elasticsearch container running
   ```

2. Ensure Ollama service is running:
   ```bash
   ollama serve  # Run in a separate terminal
   ```

3. Index your documents (if not already done):
   ```python
   # Example code to index documents will be provided in scripts/
   ```

4. Use the QA service:
   ```python
   from services.text_qa import generate_answer
   
   question = "Your question here"
   answer = generate_answer(question)
   print(answer)
   ```

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

## Configuration

- Default vector search returns top 3 documents
- Uses 'text_embeddings' as default Elasticsearch index
- Embeddings are generated using the bge-m3 model
- Text generation uses llama3.2:1b model
- Default Elasticsearch connection: `http://localhost:9200`
- Default index name: `text_embeddings`
- Vector search parameters:
  - Top-k results: 3 (configurable)
  - Embedding model: bge-m3
  - Text generation model: llama3.2:1b

## Troubleshooting

1. If Elasticsearch fails to start, check:
   - Docker is running
   - Port 9200 is not in use
   - System has enough memory (minimum 4GB recommended)

2. If Ollama fails:
   - Ensure the service is running (`ollama serve`)
   - Check if models are properly downloaded
   - Verify system has enough GPU/CPU resources

## License

[Fein Corp]

