# '''
# vectorize the pdf sections into embeddings
# '''

import os
from dotenv import load_dotenv
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
import json
load_dotenv(override = True)

# embedding_model_name = os.getenv("EMBEDDING_MODEL_NAME")
# embedding_model_endpoint = os.getenv("EMBEDDING_MODEL_ENDPOINT")
# embedding_model_key = os.getenv("EMBEDDING_MODEL_KEY")

azure_openai_endpoint = os.environ["OPENAI_ENDPOINT"]
azure_openai_key = os.getenv("OPENAI_KEY", "") if len(os.getenv("OPENAI_KEY", "")) > 0 else None
azure_openai_embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
azure_openai_embedding_dimensions = int(os.getenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS", 1024))
embedding_model_name = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2023-05-15")
openai_credential = DefaultAzureCredential()

def client(): 
    client = AzureOpenAI(
        api_key = azure_openai_key,  
        api_version = "2024-06-01",
        azure_endpoint = azure_openai_endpoint
        )
    
    return client

def generate_embeddings(input_path):
    embed_client = client()
    with open(path, 'r', encoding='utf-8') as file:
        text_data = json.load(file)
    content = [item["content"] for item in text_data]
    content_response = embed_client.embeddings.create(input = content, model = embedding_model_name, dimensions = azure_openai_embedding_dimensions)
    content_embeddings = [item.embedding for item in content_response.data]

    for i, item in enumerate(text_data):
        item["content_embedding"] = content_embeddings[i]
    
    output_path = "/Users/giangpham/Desktop/VCB/test/sections_embedding.json"
    output_directory = os.path.dirname(output_path)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    with open(output_path, "w") as f:
        json.dump(text_data, f)
    return text_data

if __name__ == "__main__":
    path = "/Users/giangpham/Desktop/VCB/test/sections.json"
    generate_embeddings(path)