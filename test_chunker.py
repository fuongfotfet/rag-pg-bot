from rag_system.components.loaders.local_loader import LocalOCRPDFLoader
from rag_system.components.chunkers.fixed_size_chunker import LangchainCompatibleChunker

def test_chunker_only(pdf_path: str):
    loader = LocalOCRPDFLoader()
    data_chunks_by_page = loader.load(pdf_path)
    print(f"📄 Số trang OCR được: {len(data_chunks_by_page)}")

    chunker = LangchainCompatibleChunker(chunk_size=1000, chunk_overlap=100)
    chunked_data = chunker.chunk(data_chunks_by_page)
    print(f"🔖 Số đoạn (chunks) sau khi chia: {len(chunked_data)}")

    for i, chunk in enumerate(chunked_data[:3]):  # In thử 3 chunk đầu
        print(f"\n--- Chunk {i} ---")
        print(f"Page: {chunk.page_number} | Offset: {chunk.offset}")
        print(chunk.content[:300])  # in 300 ký tự đầu

if __name__ == "__main__":
    test_chunker_only("data/13nd.signed.pdf")
