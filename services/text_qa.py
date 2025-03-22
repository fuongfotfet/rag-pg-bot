import os
from elasticsearch import Elasticsearch
import ollama
from sentence_transformers import CrossEncoder
import numpy as np
from typing import List, Tuple, Dict, Any

# Kết nối Elasticsearch
ELASTIC_HOST = os.getenv('ELASTIC_HOST')
ELASTIC_PORT = os.getenv('ELASTIC_PORT')
es = Elasticsearch("http://{}:{}".format(ELASTIC_HOST, ELASTIC_PORT))


def vector_search(query: str, k: int = 3, index_name: str = 'text_embeddings') -> List[Tuple[str, float]]:
    """
    Perform vector search using Elasticsearch with cosine similarity.

    Args:
        query (str): The search query text
        k (int, optional): Number of results to return. Defaults to 3.
        index_name (str, optional): Elasticsearch index name. Defaults to 'text_embeddings'.

    Returns:
        List[Tuple[str, float]]: List of tuples containing (document_text, similarity_score)
    """
    # Bước 1: Lấy embedding cho truy vấn bằng Ollama (bge-m3)
    response = ollama.embed(model='bge-m3', input=query)
    query_embedding = response['embeddings'][0]  # Lấy mảng 1D

    # Bước 2: Xây dựng truy vấn script score cho Elasticsearch
    script_query = {
        "script_score": {
            "query": {
                "match_all": {}  # Lấy tất cả các document
            },
            "script": {
                # cosineSimilarity trả về giá trị trong [-1, 1], cộng thêm 1 để có giá trị dương
                "source": "cosineSimilarity(params.queryVector, 'embedding') + 1.0",
                "params": {
                    "queryVector": query_embedding
                }
            }
        }
    }

    # Bước 3: Gửi truy vấn và lấy top-k kết quả
    res = es.search(index=index_name, query=script_query, size=k)

    # Bước 4: Trích xuất text và score từ kết quả
    hits = res['hits']['hits']
    docs = []
    for hit in hits:
        source = hit['_source']
        score = hit['_score']
        docs.append((source["text"], score))

    return docs

# --- Sliding Window Extraction ---


# Tải model cross-encoder để đánh giá relevance của các cửa sổ
reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# def sliding_window_search(chunk, question, window_size=3, threshold=0.5):
#     """
#     Tách đoạn văn (chunk) thành các cửa sổ với số câu window_size,
#     sau đó đánh giá relevance của mỗi cửa sổ với câu hỏi bằng cross-encoder.

#     Parameters:
#       - chunk: đoạn văn bản (string)
#       - question: câu hỏi (string)
#       - window_size: số câu trong mỗi cửa sổ (mặc định 3)
#       - threshold: ngưỡng để chấp nhận cửa sổ (mặc định 0.5)

#     Returns:
#       - best_window: cửa sổ có điểm cao nhất (string) hoặc thông báo nếu không đủ relevance
#       - best_score: điểm của cửa sổ đó
#     """
#     # Tách chunk thành các câu. Lưu ý: điều chỉnh ký tự phân tách nếu cần.
#     sentences = chunk.split('. ')
#     if len(sentences) < window_size:
#         windows = [" ".join(sentences)]
#     else:
#         windows = [" ".join(sentences[i:i+window_size]) for i in range(len(sentences) - window_size + 1)]

#     # Tạo cặp (question, window) cho cross-encoder
#     pairs = [(question, window) for window in windows]
#     scores = reranker.predict(pairs)

#     scores = np.array(scores)
#     best_index = int(scores.argmax())
#     best_score = float(scores[best_index])
#     best_window = windows[best_index]

#     if best_score >= threshold:
#         return best_window, best_score
#     else:
#         return "Không tìm thấy thông tin phù hợp.", best_score

# # --- Ví dụ sử dụng tích hợp cả vector_search và Sliding Window ---
# if __name__ == "__main__":
#     # Giả sử truy vấn của người dùng
#     query = "Chuyển dữ liệu ra ngước ngoài"

#     # Lấy các document có liên quan từ Elasticsearch
#     results = vector_search(query, k=3, index_name='text_embeddings')

#     print(f"🔍 Kết quả tìm kiếm cho câu hỏi: {query}\n")
#     for i, (doc_text, score) in enumerate(results, start=1):
#         print(f"Document {i}: (Score: {score:.3f})")
#         print("Full text:")
#         print(doc_text)
#         # Áp dụng chiến lược Sliding Window để lấy ra phần context phù hợp nhất
#         best_window, window_score = sliding_window_search(doc_text, query, window_size=3, threshold=0.5)
#         print("\nExtracted best window:")
#         print(best_window)
#         print(f"Window relevance score: {window_score:.3f}")
#         print("-" * 60)


# ========================================================================================================#

query = "Việc chuyển dữ liệu cá nhân ra nước ngoài"

results = vector_search(query, k=3, index_name='text_embeddings')

# In kết quả
for i, (doc_text, score) in enumerate(results, start=1):
    print(f"Document {i}:")
    print(f"Text: {doc_text}")
    print(f"Score: {score}")
    print()


def generate_answer(question: str, k: int = 3, index_name: str = 'text_embeddings') -> str:
    """
    Generate an answer for a given question using RAG approach.

    Args:
        question (str): The user's question
        k (int, optional): Number of documents to retrieve. Defaults to 3.
        index_name (str, optional): Elasticsearch index name. Defaults to 'text_embeddings'.

    Returns:
        str: Generated answer based on retrieved documents
    """
    # Bước 1: Lấy các tài liệu liên quan
    retrieved_docs = vector_search(question, k, index_name)

    # Bước 2: Chuẩn bị prompt
    # Ghép tài liệu thành 1 chuỗi context
    context_docs = "\n\n".join([f"- {doc[0]}" for doc in retrieved_docs])

    # Prompt ví dụ:
    prompt = f"""
        cho câu hỏi sau đây, Hãy đưa ra câu trả lời thân thiện hơn - và làm rõ từ tài liệu nào trang bao nhiêu
        Chỉ đưa ra câu trả lời, không nói gì hơn
        Các đoạn văn liên quan:
        {context_docs}

        Câu hỏi: {question}

        Câu trả lời:
        """
    # print("Final prompt:\n", prompt)
    # Bước 3: Gọi mô hình Ollama (hoặc mô hình khác)
    response = ollama.generate(
        model="llama3.2:1b",
        prompt=prompt
    )
    return response.get("response")


# # Ví dụ truy vấn từ người dùng:
# question = "Việc chuyển dữ liệu cá nhân ra nước ngoài"

# # Gọi hàm generate_answer
# answer = generate_answer(question, k=3, index_name='text_embeddings')

# # In kết quả nhận được
# print("Câu hỏi:", question)
# print("Câu trả lời từ mô hình:", answer)
