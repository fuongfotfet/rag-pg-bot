import ollama

class OllamaBGEClient:
    def __init__(self, model: str = "bge-m3", dimensions: int = 1024):
        self.model_name = model
        self.embedding_dimensions = dimensions

    def generate_embeddings(self, text: str) -> list:
        """
        Gửi văn bản tới mô hình Ollama và nhận về embedding.
        """
        response = ollama.embed(model=self.model_name, input=text)
        return response['embeddings'][0]

    def get_parameters(self):
        return {
            "model_name": self.model_name,
            "embedding_dimensions": self.embedding_dimensions
        }
