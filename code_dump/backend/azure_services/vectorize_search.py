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
from azure.search.documents.models import VectorizedQuery
from azure.search.documents import SearchItemPaged

load_dotenv(override=True)

class AzureSearch: 
    def __init__(self): 
        self.search_client = self.client()
        self.search_index_client = self.index_client()
        self.index_name = os.getenv("SEARCH_INDEX_NAME")
        self.search_service_endpoint = os.getenv("SEARCH_ENDPOINT")
        self.search_api_key = os.getenv("SEARCH_KEY")
        self.azure_openai_embedding_dimensions = int(os.getenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS", 1024))
        self.azure_openai_endpoint = os.environ["OPENAI_ENDPOINT"]
        self.azure_openai_key = os.getenv("EMBEDDING_MODEL_KEY", "") if len(os.getenv("EMBEDDING_MODEL_KEY", "")) > 0 else None
        self.azure_openai_embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
        self.embedding_model_name = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
    
    def client(self): 
        search_service_endpoint = os.getenv("SEARCH_ENDPOINT")
        search_index_name = os.getenv("SEARCH_INDEX_NAME")
        search_api_key = os.getenv("SEARCH_KEY")
        search_client = SearchClient(endpoint=search_service_endpoint, index_name=search_index_name, credential=AzureKeyCredential(search_api_key))
        return search_client

    def index_client(self): 
        search_service_endpoint = os.getenv("SEARCH_ENDPOINT")
        search_api_key = os.getenv("SEARCH_KEY")
        search_index_name = os.getenv("SEARCH_INDEX_NAME")
        index_client = SearchIndexClient(endpoint=search_service_endpoint, credential=AzureKeyCredential(search_api_key))
        return index_client

    def create_index(self):
        index_client = self.search_index_client
        # Step 1: Try to get the existing index
        try:
            existing_index = index_client.get_index(self.index_name)
            print(f"Index '{self.index_name}' already exists")
            return 

        except ResourceNotFoundError:
            # If the index does not exist, this will be caught and we proceed without deletion
            print(f"Index '{self.index_name}' does not exist. Proceeding to create a new one.")

        fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, sortable=True, filterable=True, facetable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchableField(name="sourcefile", type=SearchFieldDataType.String,
                        filterable=True),
        SimpleField(name="page", type=SearchFieldDataType.Int32,
                    filterable=True),
        SearchField(name="content_embedding", type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, vector_search_dimensions=self.azure_openai_embedding_dimensions, vector_search_profile_name="myHnswProfile"),
    ]
        
            # Configure the vector search configuration  
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
                        resource_url=self.azure_openai_endpoint,
                        deployment_name=self.azure_openai_embedding_deployment,
                        model_name=self.embedding_model_name,
                        api_key=self.azure_openai_key
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
        index = SearchIndex(name= self.index_name, fields=fields,
                            vector_search=vector_search, semantic_search=semantic_search)
        result = index_client.create_or_update_index(index)
        print(f'{result.name} created')
    




