from typing import Optional, Type

class DataChunk: 
    def __init__(
        self,
        content: str,
        source: str,
        offset: Optional[int] = None,
        page_number: Optional[int] = None,
        chunk_id: Optional[str] = None,
    ):
        self.content = content
        self.source = source #url of the document
        self.offset = offset
        self.page_number = page_number
        self.chunk_id = chunk_id
    
    def __str__(self): 
        return f"DataChunk: {self.source} - {self.page_number} - {self.offset} - {self.chunk_id}: {self.content}"

    def to_dictionary(self):
        return {
            "content": self.content,
            "source": self.source,
            "offset": self.offset,
            "page_number": self.page_number,
            "chunk_id": self.chunk_id,
        }