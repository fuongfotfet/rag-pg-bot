from typing import List
from rag_system.core.data_chunk import DataChunk
from .loader_base import DataLoaderBase
from pdf2image import convert_from_path
import pytesseract
from pytesseract import Output
import os

class LocalOCRPDFLoader(DataLoaderBase):
    def __init__(self, dpi: int = 300, lang: str = "vie"):
        self.dpi = dpi
        self.lang = lang

    def content_cleaning(self, content: str) -> str:
        '''
        Clean OCR text: remove empty lines and whitespace.
        '''
        return "\n".join(line for line in content.splitlines() if line.strip())

    def load(self, pdf_path: str) -> List[DataChunk]:
        '''
        Load scanned PDF using OCR (pytesseract) and return DataChunks (1 chunk = 1 page).
        '''
        pages = convert_from_path(pdf_path, dpi=self.dpi)
        data_chunks = []
        offset = 0
        for i, page in enumerate(pages):
            # OCR trang
            text = pytesseract.image_to_string(page, lang=self.lang)
            cleaned_text = self.content_cleaning(text)

            chunk = DataChunk(
                content=cleaned_text,
                source=pdf_path,
                offset=offset,
                page_number=i + 1
            )
            data_chunks.append(chunk)
            offset += len(cleaned_text)
        return data_chunks
