# rag_system/components/embedders/elasticsearch_embedder.py

from .embedder_base import EmbedderBase
from rag_system.services.ollama_embedder import OllamaBGEClient
from rag_system.core.data_chunk import DataChunk
from typing import List
from rag_system.services.elasticsearch_store import ElasticsearchVectorStore
import os

class OllamaEmbedder(EmbedderBase):
    def __init__(self, index_name: str = "text_embeddings"):
        # Embedder: bge-m3 via Ollama
        self.embed_client = OllamaBGEClient()
        self.index_name = index_name
        # Vector DB: Elasticsearch
        self.vector_store = ElasticsearchVectorStore(index_name=index_name, dim=self.embed_client.embedding_dimensions)

    def embed(self, text: str) -> List[float]: 
        '''
        Sinh embedding bằng bge-m3
        '''
        return self.embed_client.generate_embeddings(text)
    
    def embed_and_load(self, data: List[DataChunk]) -> None:
        '''
        Sinh embedding và đẩy toàn bộ data vào Elasticsearch
        '''
        try:
            self.vector_store.create_index()

            contents = [d.content for d in data]
            embeddings = [self.embed(c) for c in contents]
            print(f"🧠 Đã sinh {len(embeddings)} embedding")

            all_data_chunk = [item.to_dictionary() for item in data]
            for i, item in enumerate(all_data_chunk):
                item["text"] = item["content"]
                item["embedding"] = embeddings[i]
                item["chunk_id"] = item.get("chunk_id") or f"chunk_{i}"

            self.vector_store.upload_embeddings(all_data_chunk)
            print("✅ Successfully uploaded embedded data to Elasticsearch.")

        except Exception as e:
            print(f"❌ Lỗi khi embed và upload: {str(e)}")
