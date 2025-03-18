import openai
from elasticsearch import Elasticsearch
import os

# Thiết lập OpenAI API Key (Đặt biến môi trường hoặc hardcode ở đây)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
openai.api_key = OPENAI_API_KEY

# Kết nối Elasticsearch
es = Elasticsearch("http://localhost:9200")

print("Connected to Elasticsearch")

# Tạo index với text-embedding-3-large (1536 dimensions)
index_name = 'text_embeddings_openai'
mapping = {
    "mappings": {
        "properties": {
            "text": {"type": "text"},
            "embedding": {"type": "dense_vector", "dims": 3072}  # text-embedding-3-large có 1536 dimensions
        }
    }
}

# Xóa và tạo lại index
if es.indices.exists(index=index_name):
    es.indices.delete(index=index_name, ignore=[400, 404])  
es.indices.create(index=index_name, body=mapping)