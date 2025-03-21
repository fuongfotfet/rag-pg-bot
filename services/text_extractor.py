# module0.py
from pdf2image import convert_from_path
import pytesseract
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List

def get_documents_from_pdf(local_path: str, dpi: int = 300) -> List[Document]:
    """
    Convert PDF file to Documents with extracted text and metadata.

    Args:
        local_path (str): Path to the PDF file
        dpi (int, optional): DPI for PDF rendering. Defaults to 300.

    Returns:
        List[Document]: List of Document objects containing page text and metadata
    """
    pages = convert_from_path(local_path, dpi=dpi)
    documents = []
    for i, page in enumerate(pages):
        text = pytesseract.image_to_string(page, lang='vie')
        metadata = {"page": i + 1, "source": local_path}
        documents.append(
            Document(page_content=f"--- Trang {i+1} ---\n{text}", metadata=metadata))
    return documents

def get_chunked_documents_from_pdf(
    local_path: str, 
    dpi: int = 300, 
    chunk_size: int = 1000, 
    chunk_overlap: int = 100
) -> List[Document]:
    """
    Extract and chunk PDF content into smaller Document objects.

    Args:
        local_path (str): Path to the PDF file
        dpi (int, optional): DPI for PDF rendering. Defaults to 300.
        chunk_size (int, optional): Maximum size of each chunk. Defaults to 1000.
        chunk_overlap (int, optional): Overlap between chunks. Defaults to 100.

    Returns:
        List[Document]: List of chunked Document objects
    """
    # Lấy các Document gốc từ file PDF
    documents = get_documents_from_pdf(local_path, dpi)
    # Khởi tạo text splitter với các tham số cho trước
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    # Chia nhỏ các Document thành các chunk
    docs_split = splitter.split_documents(documents)
    return docs_split

if __name__ == "__main__":
    # Ví dụ chạy thử khi module0 được thực thi trực tiếp
    local_path = "data/13nd.signed.pdf"
    docs_split = get_chunked_documents_from_pdf(local_path)
    for i, doc in enumerate(docs_split):
        print(f"Document {i}:")
        print("Attributes:", vars(doc))
        print("Content:", doc.page_content[:200], "...\n")
