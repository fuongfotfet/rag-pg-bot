import os 
from dotenv import load_dotenv
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import (
    SimpleField,
    SearchFieldDataType,
    SearchableField,
    SearchField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    SemanticSearch,
    SearchIndex,
    AzureOpenAIVectorizer,
    AzureOpenAIVectorizerParameters
)
from azure.search.documents import SearchClient
import json
from azure.core.exceptions import ResourceNotFoundError
from vectorize import client
from azure.search.documents.models import VectorizedQuery, VectorizableTextQuery
from azure.search.documents import SearchItemPaged

load_dotenv(override=True)
search_service_endpoint = os.getenv("SEARCH_ENDPOINT")
search_serive_key = os.getenv("SEARCH_KEY")
search_index_name = os.getenv("SEARCH_INDEX_NAME")
azure_openai_embedding_dimensions = int(os.getenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS", 1024))
azure_openai_endpoint = os.environ["OPENAI_ENDPOINT"]
azure_openai_key = os.getenv("EMBEDDING_MODEL_KEY", "") if len(os.getenv("EMBEDDING_MODEL_KEY", "")) > 0 else None
azure_openai_embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
embedding_model_name = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")

def create_index_client(): 
    return SearchIndexClient(endpoint=search_service_endpoint, credential=AzureKeyCredential(search_serive_key))

def create_search_client(): 
    return SearchClient(endpoint=search_service_endpoint, index_name=search_index_name, credential=AzureKeyCredential(search_serive_key))

def create_index(): 
    index_client = create_index_client()
        # Step 1: Try to get the existing index
    try:
        existing_index = index_client.get_index(search_index_name)
        print(f"Index '{search_index_name}' exists. Deleting it.")

        # Step 2: If the index exists, delete it
        index_client.delete_index(search_index_name)
        print(f"Index '{search_index_name}' deleted.")

    except ResourceNotFoundError:
        # If the index does not exist, this will be caught and we proceed without deletion
        print(f"Index '{search_index_name}' does not exist. Proceeding to create a new one.")

    fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SearchableField(name="sourcefile", type=SearchFieldDataType.String,
                    filterable=True),
    SimpleField(name="page", type=SearchFieldDataType.Int32,
                filterable=True),
    SearchField(name="content_embedding", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True, vector_search_dimensions=azure_openai_embedding_dimensions, vector_search_profile_name="myHnswProfile"),
]
    
        # Vector search configuration  
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="myHnsw"
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
                vectorizer_name="myVectorizer"
            )
        ],
        vectorizers=[
            AzureOpenAIVectorizer(
                vectorizer_name="myVectorizer",
                parameters=AzureOpenAIVectorizerParameters(
                    resource_url=azure_openai_endpoint,
                    deployment_name=azure_openai_embedding_deployment,
                    model_name=embedding_model_name,
                    api_key=azure_openai_key
                )
            )
        ]
    )

    semantic_config = SemanticConfiguration(
        name="my-semantic-config",
        prioritized_fields=SemanticPrioritizedFields(
            content_fields=[SemanticField(field_name="content")]
        )
    )

    # Create the semantic settings with the configuration
    semantic_search = SemanticSearch(configurations=[semantic_config])

    # Create the search index with the semantic settings
    index = SearchIndex(name=search_index_name, fields=fields,
                        vector_search=vector_search, semantic_search=semantic_search)
    result = index_client.create_or_update_index(index)
    print(f'{result.name} created')

def insert_embeddings(json_path): 
    output_directory = os.path.dirname(json_path)
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    with open(json_path, 'r') as file:  
        documents = json.load(file)  

    search_client = create_search_client()
    result = search_client.upload_documents(documents=documents)
    print(f"Uploaded {len(documents)} documents") 

# Helper code to print results
def return_results(results: SearchItemPaged[dict]):
    readable_results = []
    semantic_answers = results.get_answers()
    if semantic_answers:
        for answer in semantic_answers:
            if answer.highlights:
                print(f"Semantic Answer: {answer.highlights}")
            else:
                print(f"Semantic Answer: {answer.text}")
            print(f"Semantic Answer Score: {answer.score}\n")

    for result in results:
        print(result)
    
def search(query): 
    embed_client = client()
    query_embedding = embed_client.embeddings.create(input=query, model=embedding_model_name, dimensions=azure_openai_embedding_dimensions).data[0].embedding
    vector_query = VectorizedQuery(vector=query_embedding, k_nearest_neighbors=50, fields="content_embedding")
    search_client = create_search_client()
    
    results = search_client.search(  
    search_text=None,  
    vector_queries= [vector_query],
    select=["content", "page", "sourcefile"],
    top=2
)  

    readable_results = []
    # semantic_answers = results.get_answers()
    for result in results: 
        readable_results.append(result)
    return readable_results

def schema_inspections(): 
    index_client = create_index_client()
    index = index_client.get_index(search_index_name)
    for field in index.fields:
        print(f"Name: {field.name}")
        print(f"Type: {field.type}")
        print(f"Searchable: {field.searchable}")
        print(f"Filterable: {field.filterable}")
        print(f"Sortable: {field.sortable}")
        print(f"Facetable: {field.facetable}")
        print(f"Key: {field.key}")
        print("-" * 40)

def document_inspections(): 
    search_client = create_search_client()
    results = search_client.search(search_text="*", top=10)
    for result in results:
        print(result)

if __name__ == "__main__":
    # create_index()
    # json_path = "/Users/giangpham/Desktop/VCB/test/sections_embedding.json"
    # insert_embeddings(json_path)
    # schema_inspections()
    # document_inspections()
    query = "What does GFF stands for?"
    print(search(query))

