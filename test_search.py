# Description: This file contains the test cases for the loader module.
from rag_system.components.llm_response.generate_response import LLMResponseGenerator

def test_search():
    searcher = LLMResponseGenerator()
    index_name = "dama_index"
    user_query = "What does GFF stand for?"
    searcher.generate_response(index_name, user_query)

if __name__ == "__main__":
    test_search()