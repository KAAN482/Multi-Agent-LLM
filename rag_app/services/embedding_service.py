from sentence_transformers import SentenceTransformer
from typing import List
import logging

# Transformer uyarılarını gizle
logging.getLogger("transformers").setLevel(logging.ERROR)

# Model İsmi (Sabit)
# Model İsmi (Sabit)
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

class EmbeddingService:
    """
    Metinleri vektörlere dönüştüren servis.
    'intfloat/multilingual-e5-base' modelini kullanır.
    """
    def __init__(self):
        """
        Modeli başlatır. İlk çalıştırmada modeli indirir.
        """
        print(f"Embedding modeli yükleniyor: {MODEL_NAME}...")
        # VRAM tasarrufu için CPU'ya zorluyoruz
        self.model = SentenceTransformer(MODEL_NAME, device="cpu")
        print("Model hazır.")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Doküman parçalarını (chunk) vektörleştirir.
        E5 modeli için dokümanlara 'passage: ' öneki eklenmesi önerilir.
        """
        # E5 modeli için prefix ekleyelim
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Sorguyu vektörleştirir.
        E5 modeli için sorgulara 'query: ' öneki eklenmesi gerekir.
        """
        embedding = self.model.encode(query, normalize_embeddings=True)
        return embedding.tolist()

# Singleton instance (Uygulama genelinde tek bir model instance'ı kullanılır)
embedding_service = EmbeddingService()
