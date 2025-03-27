#this class is responsible for searching the answer to the question using Azure Search
from rag_system.components.search.search_base import SearchBase
from rag_system.services.azure_ai_search import AzureAISearch

class AzureSearch(SearchBase): 
    def __init__(self): 
        self.search_client = AzureAISearch()

    def search(self, index_name, question):
        return self.search_client.semantic_search(index_name, question)
    