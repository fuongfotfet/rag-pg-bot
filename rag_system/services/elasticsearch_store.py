import os
from elasticsearch import Elasticsearch
from elasticsearch.helpers import bulk
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv(override=True)

class ElasticsearchVectorStore:
    def __init__(self, index_name: str = "text_embeddings", dim: int = 1024):
        self.index_name = index_name
        self.dim = dim
        self.host = os.getenv("ELASTIC_HOST", "localhost")
        self.port = os.getenv("ELASTIC_PORT", "9200")
        self.es = Elasticsearch(f"http://{self.host}:{self.port}")
        print(f"✅ Connected to Elasticsearch at {self.host}:{self.port}")
    
    def create_index(self, show_fields=False):
        """
        Tạo index với mapping phù hợp cho vector search.
        """
        if self.es.indices.exists(index=self.index_name):
            print(f"⚠️ Index '{self.index_name}' đã tồn tại.")
            return

        mapping = {
            "mappings": {
                "properties": {
                    "chunk_id": {"type": "keyword"},
                    "text": {"type": "text"},
                    "source": {"type": "keyword"},
                    "page_number": {"type": "integer"},
                    "offset": {"type": "integer"},
                    "embedding": {
                        "type": "dense_vector",
                        "dims": self.dim,
                        "index": True,
                        "similarity": "cosine"
                    }
                }
            }
        }

        self.es.indices.create(index=self.index_name, body=mapping)
        print(f"✅ Index '{self.index_name}' đã được tạo.")

        if show_fields:
            index_info = self.es.indices.get_mapping(index=self.index_name)
            fields = index_info[self.index_name]['mappings']['properties']
            print("📌 Các field trong index:")
            for field_name, field_info in fields.items():
                print(f" - {field_name}: {field_info['type']}")

    def delete_index(self):
        if self.es.indices.exists(index=self.index_name):
            self.es.indices.delete(index=self.index_name)
            print(f"🗑️ Đã xóa index '{self.index_name}'")

    def upload_embeddings(self, data: List[Dict]):
        """
        Upload danh sách document dạng:
        {
          "chunk_id": str,
          "text": str,
          "source": str,
          "page_number": int,
          "offset": int,
          "embedding": List[float]  # 1024 chiều
        }
        """
        actions = [
            {
                "_index": self.index_name,
                "_source": doc
            }
            for doc in data
        ]
        bulk(self.es, actions)
        print(f"📤 Uploaded {len(actions)} documents to index '{self.index_name}'")

    def semantic_search(self, query_vector: List[float], k: int = 5) -> List[Dict]:
        """
        Truy vấn vector (semantic search) với cosine similarity.
        """
        query = {
            "size": k,
            "query": {
                "script_score": {
                    "query": {"match_all": {}},
                    "script": {
                        "source": "cosineSimilarity(params.query_vector, 'embedding') + 1.0",
                        "params": {"query_vector": query_vector}
                    }
                }
            }
        }

        response = self.es.search(index=self.index_name, body=query)
        return [
            {
                "text": hit["_source"].get("text"),
                "source": hit["_source"].get("source"),
                "page_number": hit["_source"].get("page_number"),
                "score": hit["_score"]
            }
            for hit in response["hits"]["hits"]
        ]
