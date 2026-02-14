from sentence_transformers import SentenceTransformer
import os

MODEL_NAME = "intfloat/multilingual-e5-base"

print(f"Downloading/Loading model: {MODEL_NAME}...")
try:
    model = SentenceTransformer(MODEL_NAME)
    print("Model successfully loaded!")
    
    # Test embedding
    embeddings = model.encode(["test query"])
    print(f"Test embedding shape: {embeddings.shape}")
except Exception as e:
    print(f"Error loading model: {e}")
