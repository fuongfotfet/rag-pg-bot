from elasticsearch import Elasticsearch
import ollama

es = Elasticsearch(
    "http://localhost:9200"
)

def vector_search(query, k=3, index_name='text_embeddings'):
    # Bước 1: Lấy embedding cho truy vấn
    response = ollama.embed(model='bge-m3', input=query)
    query_embedding = response['embeddings'][0]  # Mảng 1D

    # Bước 2: Xây dựng script query cho Elasticsearch
    script_query = {
        "script_score": {
            "query": {
                "match_all": {}  # Lọc match_all để lấy toàn bộ docs, sau đó chấm điểm bằng vector
            },
            "script": {
                # cosinesim(queryVector, docVector) trả ra [-1..1], ta +1 để tránh số âm
                "source": "cosineSimilarity(params.queryVector, 'embedding') + 1.0",
                "params": {
                    "queryVector": query_embedding
                }
            }
        }
    }

    # Bước 3: Gửi truy vấn, lấy top-k kết quả
    res = es.search(index=index_name, query=script_query, size=k)

    # Bước 4: Trích ra text và điểm
    hits = res['hits']['hits']
    docs = []
    for hit in hits:
        source = hit['_source']
        score = hit['_score']
        docs.append((source["text"], score))

    return docs

# query = "Why is the sky blue?"

# results = vector_search(query, k=3, index_name='text_embeddings')

# # In kết quả
# for i, (doc_text, score) in enumerate(results, start=1):
#     print(f"Document {i}:")
#     print(f"Text: {doc_text}")
#     print(f"Score: {score}")
#     print()
    
def generate_answer(question, k=3, index_name='text_embeddings'):
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
    print("Final prompt:\n", prompt)
    # Bước 3: Gọi mô hình Ollama (hoặc mô hình khác)
    response = ollama.generate(
        model="llama3.2:1b",    
        prompt=prompt
    )
    return response


# Ví dụ truy vấn từ người dùng:
question = "dữ liệu cá nhân là gì?"

# Gọi hàm generate_answer
answer = generate_answer(question, k=3, index_name='text_embeddings')

# In kết quả nhận được
print("Câu hỏi:", question)
print("Câu trả lời từ mô hình:", answer)