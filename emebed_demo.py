import ollama
import numpy as np
import sys

text1 = sys.argv[1]
text2 = sys.argv[2]

def semantic_similarity(text1: str, text2: str, model='nomic-embed-text'):
    # Compute embeddings for both strings
    emb1 = ollama.embeddings(model=model, prompt=text1)['embedding']
    emb2 = ollama.embeddings(model=model, prompt=text2)['embedding']
    
    # Convert to numpy arrays
    vec1 = np.array(emb1)
    vec2 = np.array(emb2)
    
    # Calculate cosine similarity
    similarity = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
    
    return similarity

# Example usage:
text_a = "The sky is blue because of rayleigh scattering"
text_b = "Blue skies result from the scattering of sunlight in Earth's atmosphere"

similarity_score = semantic_similarity(text1, text2, "bge-m3")
print(f"Similarity score: {similarity_score:.4f}")
