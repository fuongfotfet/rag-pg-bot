import openai
from elasticsearch import Elasticsearch
import os
from dotenv import load_dotenv

load_dotenv()

# Thiết lập OpenAI API Key (Đặt biến môi trường hoặc hardcode ở đây)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
openai.api_key = OPENAI_API_KEY

# Kết nối Elasticsearch
es = Elasticsearch("http://localhost:9200")

print("Connected to Elasticsearch")

def get_embedding(text):
    """
    Lấy embedding từ mô hình text-embedding-3-large của OpenAI.
    """
    response = openai.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    return response.data[0].embedding  # Trả về vector embedding

def vector_search(query, k=3, index_name='text_embeddings_openai'):
    """
    Tìm kiếm vector bằng Elasticsearch, sử dụng cosine similarity.
    """
    query_embedding = get_embedding(query)

    # Xây dựng truy vấn script score
    script_query = {
        "script_score": {
            "query": {
                "match_all": {}  # Lấy tất cả docs, tính điểm theo vector similarity
            },
            "script": {
                "source": "cosineSimilarity(params.queryVector, 'embedding') + 1.0",
                "params": {
                    "queryVector": query_embedding
                }
            }
        }
    }

    # Gửi truy vấn tới Elasticsearch
    res = es.search(index=index_name, query=script_query, size=k)

    # Trích xuất kết quả
    hits = res['hits']['hits']
    docs = [(hit['_source']['text'], hit['_score']) for hit in hits]
    
    return docs

def generate_answer(question, k=3, index_name='text_embeddings_openai'):
    """
    Sinh câu trả lời dựa trên tài liệu từ Elasticsearch và GPT-4o-mini.
    """
    retrieved_docs = vector_search(question, k, index_name)

    # Ghép các tài liệu thành prompt cho GPT-4o-mini
    context_docs = "\n\n".join([f"- {doc[0]}" for doc in retrieved_docs])

    prompt = f"""
Bạn hãy trả lời câu hỏi dựa trên chỉ dựa vào các đoạn văn dưới đây, không trả lời những thông tin không liên quan:
{context_docs}

Câu hỏi: {question}

Câu trả lời:
"""

    # Gọi GPT-4o-mini để sinh câu trả lời
    response = openai.chat.completions.create(
        model="gpt-4o-mini",  # Sử dụng GPT-4o-mini thay vì LLaMA
        messages=[{"role": "system", "content": ("Bạn là trợ lý chuyên gia trong việc trích xuất thông tin từ một văn bản cho trước."
                                                 + "Hãy cung cấp chính xác tên file mà bạn đã trích xuất")},
                  {"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content  # Trả về nội dung trả lời

# Ví dụ truy vấn
question = "Dữ liệu cá nhân trong Nghị Định được định nghĩa là gì?"
answer = generate_answer(question, k=3, index_name='text_embeddings_openai')

results = vector_search(question, k=3, index_name="text_embeddings_openai")

# # In kết quả
# print(f"\n🔍 Kết quả tìm kiếm cho: {question}")
# for i, (doc_text, score) in enumerate(results, start=1):
#     print(f"\n📌 Document {i}:")
#     print(f"📝 Nội dung: {doc_text}")
#     print(f"⭐ Score: {score}")

# In kết quả
print("Câu hỏi:", question)
print("Câu trả lời từ mô hình:", answer)