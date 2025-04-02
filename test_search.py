# Description: This file contains the test cases for the loader module.
from rag_system.components.llm_response.generate_response import LLMResponseGenerator

def test_search():
    searcher = LLMResponseGenerator()
    chat_history = []
    index_name = "text_embeddings"
    user_query = "dữ liệu cá nhân là gì?"
    searcher.generate_response(index_name, user_query, chat_history)

if __name__ == "__main__":
    test_search()