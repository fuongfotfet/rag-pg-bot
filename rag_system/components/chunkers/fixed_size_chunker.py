from typing import List
from rag_system.components.chunkers.chunker_base import ChunkerBase
from rag_system.core.data_chunk import DataChunk
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

class LangchainCompatibleChunker(ChunkerBase):
    def __init__(self, chunk_size=1000, chunk_overlap=100):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap
        )

    def chunk(self, data: List[DataChunk]) -> List[DataChunk]:
        """
        Nhận list DataChunk (theo từng trang), chuyển sang Document (LangChain),
        chunk bằng RecursiveCharacterTextSplitter, rồi trả lại list DataChunk.
        """
        # B1: chuyển sang Document
        docs = []
        for chunk in data:
            docs.append(Document(
                page_content=chunk.content,
                metadata={
                    "source": chunk.source,
                    "page": chunk.page_number,
                    "offset": chunk.offset
                }
            ))

        # B2: chunk văn bản
        split_docs = self.splitter.split_documents(docs)

        # B3: chuyển ngược về DataChunk
        result = []
        for i, doc in enumerate(split_docs):
            result.append(DataChunk(
                content=doc.page_content,
                source=doc.metadata.get("source"),
                page_number=doc.metadata.get("page"),
                offset=doc.metadata.get("offset"),
                chunk_id=f"{doc.metadata.get('source').split('/')[-1]}-chunk-{i}"
            ))

        return result
