# Description: This file contains the test cases for the loader module using Ollama + Elasticsearch.

from rag_system.components.loaders.local_loader import LocalOCRPDFLoader
from rag_system.components.chunkers.fixed_size_chunker import LangchainCompatibleChunker
from rag_system.components.embedders.ollama_embedder import OllamaEmbedder

def test_loader(url):
    loader = LocalOCRPDFLoader()
    data_chunks_by_page = loader.load(url)
    assert len(data_chunks_by_page) > 0
    print(f"📄 OCR được {len(data_chunks_by_page)} trang.")

    chunker = LangchainCompatibleChunker()
    chunked_data = chunker.chunk(data_chunks_by_page)
    print(f"🔖 Chunk thành {len(chunked_data)} đoạn.")

    embedder = OllamaEmbedder(index_name="text_embeddings")  
    embedder.embed_and_load(chunked_data)

if __name__ == "__main__":
    url = "data/small.pdf" 
    test_loader(url)
