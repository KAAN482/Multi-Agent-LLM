from sentence_transformers import SentenceTransformer
from typing import List

# Model İsmi (Sabit)
MODEL_NAME = "intfloat/multilingual-e5-base"

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
        self.model = SentenceTransformer(MODEL_NAME)
        print("Model hazır.")

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Doküman parçalarını (chunk) vektörleştirir.
        E5 modeli için dokümanlara 'passage: ' öneki eklenmesi önerilir.
        """
        # E5 modeli için prefix ekleyelim
        formatted_texts = [f"passage: {t}" for t in texts]
        embeddings = self.model.encode(formatted_texts, normalize_embeddings=True)
        return embeddings.tolist()

    def embed_query(self, query: str) -> List[float]:
        """
        Sorguyu vektörleştirir.
        E5 modeli için sorgulara 'query: ' öneki eklenmesi gerekir.
        """
        formatted_query = f"query: {query}"
        embedding = self.model.encode(formatted_query, normalize_embeddings=True)
        return embedding.tolist()

# Singleton instance (Uygulama genelinde tek bir model instance'ı kullanılır)
embedding_service = EmbeddingService()
