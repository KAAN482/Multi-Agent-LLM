import faiss
import pickle
import os
import numpy as np

# Sabitler
INDEX_FILE = "faiss_index.bin"
METADATA_FILE = "metadata.pkl"
DIMENSION = 768  # E5-base boyutu

class VectorStore:
    """
    FAISS tabanlı vektör veritabanı yönetim sınıfı.
    Vektörleri ve ilgili metadataları (dosya adı, metin) saklar.
    """
    def __init__(self, index_path=INDEX_FILE, metadata_path=METADATA_FILE):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.index = None
        self.metadata = []  # Metadata listesi
        self._load_index()

    def _load_index(self):
        """Diskteki indeksi yükler veya yeni oluşturur."""
        if os.path.exists(self.index_path) and os.path.exists(self.metadata_path):
            print("Mevcut Vektör DB yükleniyor...")
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
        else:
            print("Yeni Vektör DB oluşturuluyor...")
            self.index = faiss.IndexFlatIP(DIMENSION)  # Cosine Similarity (inner product & normalized vectors)

    def add_documents(self, embeddings: list, metas: list):
        """
        Veritabanına yeni dokümanlar ekler.
        embeddings: Vektör listesi
        metas: Metadata listesi (dict)
        """
        if not embeddings:
            return
        
        vectors = np.array(embeddings).astype('float32')
        self.index.add(vectors)
        self.metadata.extend(metas)
        self._save_index()
        print(f"{len(embeddings)} chunk eklendi.")

    def search(self, query_embedding: list, k=3):
        """
        Vektör araması yapar.
        query_embedding: Sorgu vektörü
        k: Döndürülecek en yakın sonuç sayısı
        """
        if self.index.ntotal == 0:
            return []
            
        query_vec = np.array([query_embedding]).astype('float32')
        scores, indices = self.index.search(query_vec, k)
        
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx != -1:
                meta = self.metadata[idx]
                results.append({
                    "filename": meta['filename'],
                    "text": meta['text'],
                    "score": float(score)
                })
        return results

    def _save_index(self):
        """İndeksi ve metadatayı diske kaydeder."""
        faiss.write_index(self.index, self.index_path)
        with open(self.metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)

    def list_files(self):
        """İndekslenmiş benzersiz dosya isimlerini döndürür"""
        files = {m['filename'] for m in self.metadata}
        return list(files)

    def reset(self):
        """Veritabanını sıfırlar ve diskteki dosyaları siler."""
        print("Vektör DB sıfırlanıyor...")
        self.index = faiss.IndexFlatIP(DIMENSION)
        self.metadata = []
        if os.path.exists(self.index_path):
            os.remove(self.index_path)
        if os.path.exists(self.metadata_path):
            os.remove(self.metadata_path)
        print("Vektör DB temizlendi.")

# Singleton instance
vector_store = VectorStore()
