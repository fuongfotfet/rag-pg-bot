import ollama
from elasticsearch import Elasticsearch
from services.text_extractor import get_chunked_documents_from_pdf
from typing import Dict, Any

# Initialize Elasticsearch client
es = Elasticsearch("http://localhost:9200")


def vectorize_and_store(text: str, model: str = 'bge-m3', index_name: str = 'text_embeddings') -> None:
    """
    Generate embedding for text and store in Elasticsearch.

    Args:
        text (str): Input text to vectorize
        model (str, optional): Model name for embedding generation. Defaults to 'bge-m3'.
        index_name (str, optional): Elasticsearch index name. Defaults to 'text_embeddings'.

    Returns:
        None
    """
    # Generate embedding
    response = ollama.embed(model=model, input=text)
    # print("Response from API:", response)
    embedding = response['embeddings'][0]  # Lấy mảng 1D có 1024 giá trị

    # Index document in Elasticsearch
    document = {
        'text': text,
        'embedding': embedding
    }
    es.index(index=index_name, body=document)


pdf_path = "data/13nd.signed.pdf"
# Chunking PDF file
docs_split = get_chunked_documents_from_pdf(
    pdf_path, dpi=300, chunk_size=1000, chunk_overlap=100)

# Push to ElasticSearch
for i, doc in enumerate(docs_split):
    print(f"Indexing chunk {i} ...")
    vectorize_and_store(doc.page_content)


# # Example usage
# text = """Trong Nghị định này, các từ ngữ dưới đây được hiểu như sau:

# 1. Dữ liệu cá nhân là thông tin dưới dạng ký hiệu, chữ viết, chữ số, hình ảnh, âm thanh hoặc dạng tương tự trên môi trường điện tử gắn liền với một con người cụ thể hoặc giúp xác định một con người cụ thể. Dữ liệu cá nhân bao gồm dữ liệu cá nhân cơ bản và dữ liệu cá nhân nhạy cảm.

# 2. Thông tin giúp xác định một con người cụ thể là thông tin hình thành từ hoạt động của cá nhân mà khi kết hợp với các dữ liệu, thông tin lưu trữ khác có thể xác định một con người cụ thể.

# 3. Dữ liệu cá nhân cơ bản bao gồm:

# a) Họ, chữ đệm và tên khai sinh, tên gọi khác (nếu có);

# b) Ngày, tháng, năm sinh; ngày, tháng, năm chết hoặc mất tích;

# c) Giới tính;

# d) Nơi sinh, nơi đăng ký khai sinh, nơi thường trú, nơi tạm trú, nơi ở hiện tại, quê quán, địa chỉ liên hệ;

# đ) Quốc tịch;

# e) Hình ảnh của cá nhân;

# g) Số điện thoại, số chứng minh nhân dân, số định danh cá nhân, số hộ chiếu, số giấy phép lái xe, số biển số xe, số mã số thuế cá nhân, số bảo hiểm xã hội, số thẻ bảo hiểm y tế;

# h) Tình trạng hôn nhân;

# i) Thông tin về mối quan hệ gia đình (cha mẹ, con cái);

# k) Thông tin về tài khoản số của cá nhân; dữ liệu cá nhân phản ánh hoạt động, lịch sử hoạt động trên không gian mạng;"""
# vectorize_and_store(text)
