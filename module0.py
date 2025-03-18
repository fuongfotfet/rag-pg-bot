# module0.py
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
from langchain.docstore.document import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

def get_documents_from_pdf(local_path, dpi=300):
    """
    Đọc file PDF và chuyển mỗi trang thành một Document với metadata
    """
    pages = convert_from_path(local_path, dpi=dpi)
    documents = []
    for i, page in enumerate(pages):
        text = pytesseract.image_to_string(page, lang='vie')
        metadata = {"page": i + 1, "source": local_path}
        documents.append(Document(page_content=f"--- Trang {i+1} ---\n{text}", metadata=metadata))
    return documents

def get_chunked_documents_from_pdf(local_path, dpi=300, chunk_size=1000, chunk_overlap=100):
    """
    Lấy các Document từ PDF và chia nhỏ (chunk) nội dung của chúng
    dựa trên chunk_size và chunk_overlap.
    """
    # Lấy các Document gốc từ file PDF
    documents = get_documents_from_pdf(local_path, dpi)
    # Khởi tạo text splitter với các tham số cho trước
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
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