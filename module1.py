import openai, os
from elasticsearch import Elasticsearch
from dotenv import load_dotenv
load_dotenv()

# Initialize Elasticsearch client
es = Elasticsearch("http://localhost:9200")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-api-key")
openai.api_key = OPENAI_API_KEY

def get_embedding(text):
    """
    Lấy embedding từ mô hình text-embedding-3-large của OpenAI.
    """
    response = openai.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    print(len(response.data[0].embedding))
    return response.data[0].embedding  # Trả về vector embedding

def vectorize_and_store(text, index_name='text_embeddings_openai'):
    """
    Chuyển văn bản thành embedding và lưu vào Elasticsearch.
    """
    # Lấy embedding từ OpenAI
    embedding = get_embedding(text)
    
    # Chuẩn bị document lưu vào Elasticsearch
    document = {
        'text': text,
        'embedding': embedding
    }

    # Lưu vào Elasticsearch
    es.index(index=index_name, body=document)
    print(f"Document indexed successfully: {text[:50]}...")  # Chỉ in 50 ký tự đầu

# ===========================
# Ví dụ sử dụng module
# ===========================
if __name__ == "__main__":
    text = "Tế bào là đơn vị cơ bản của sự sống. Chúng chứa các thành phần như nhân, màng tế bào, ti thể và ribosome, giúp duy trì các chức năng sinh học quan trọng. Quá trình phân chia tế bào giúp cơ thể phát triển và tái tạo."
    
    vectorize_and_store(text)