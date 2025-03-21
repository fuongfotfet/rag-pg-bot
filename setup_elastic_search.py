from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch("http://localhost:9200")

print("connected")

# Define index mapping
index_name = 'test'
mapping = {
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            # BGE-M3 produces 1024-dimensional embeddings
            "embedding": {"type": "dense_vector", "dims": 1024}
        }
    }
}

# Create index if it doesn't exist
if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=mapping)

# Create new index
es.indices.delete(index="text_embeddings", ignore=[400, 404])
es.indices.create(index="text_embeddings", body=mapping)
