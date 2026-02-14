import os
import shutil
import io
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List

# Servisler ve Yardımcılar
from rag_app.services.rag_engine import process_query
from rag_app.services.vector_store import vector_store
from rag_app.services.embedding_service import embedding_service
from rag_app.utils.text_processing import extract_text_from_file, chunk_text

# FastAPI Uygulaması
app = FastAPI(title="Akıllı Doküman Asistanı", description="RAG tabanlı doküman ve web arama asistanı", version="1.1.0")

# Statik Dosyalar (Frontend)
app.mount("/static", StaticFiles(directory="rag_app/static"), name="static")

# Request Modelleri
class QueryRequest(BaseModel):
    question: str

class FileListResponse(BaseModel):
    files: List[str]

@app.get("/")
async def read_root():
    """Anasayfa: Frontend arayüzünü sunar."""
    return FileResponse("rag_app/static/index.html")

@app.post("/upload")
async def upload_files(files: list[UploadFile]):
    """
    Dosya Yükleme Endpoint'i:
    - PDF, DOCX, TXT dosyalarını kabul eder.
    - Metinleri çıkarır, parçalar (chunking) ve vektör veritabanına kaydeder.
    """
    processed_count = 0
    errors = []
    
    for file in files:
        filename = file.filename.lower()
        if filename.endswith((".pdf", ".docx", ".txt")):
            try:
                # Metin Çıkarımı
                # File objesini okuyup bytes olarak gönderiyoruz, extract_file içinde BytesIO ile işlenecek
                # Ancak UploadFile zaten stream benzeri davranır ama await read() ile content'i alıp işlemek daha güvenli burada.
                # text_processing.py içinde extract_lines fonksiyonunu güncelledim.
                content = await file.read()
                
                # Geçici bir UploadFile benzeri yapı veya direkt content göndermemiz gerekebilir.
                # text_processing.py update edildi mi? Evet. extract_text_from_file(file) bekliyor.
                # UploadFile'ı tekrar sarmalayalım veya seek(0) yapalım.
                # await file.seek(0) # UploadFile seekable'dır.
                
                # UploadFile nesnesini olduğu gibi gönderelim, processing içinde read yapılıyor.
                # Ancak az önce read() yaptık, cursor sonda. Başa alalım.
                await file.seek(0) 
                
                text = await extract_text_from_file(file)
                
                if not text.strip():
                    errors.append(f"{file.filename}: Boş veya okunamayan dosya.")
                    continue

                # Parçalama (Chunking)
                chunks = chunk_text(text)
                
                # Embedding Oluşturma
                embeddings = embedding_service.embed_documents(chunks)
                
                # Metadata Hazırlığı
                metas = [{"filename": file.filename, "text": c} for c in chunks]
                
                # Vektör Veritabanına Ekleme
                vector_store.add_documents(embeddings, metas)
                processed_count += 1
                
            except Exception as e:
                print(f"Hata ({file.filename}): {e}")
                errors.append(f"{file.filename}: {str(e)}")
        else:
            errors.append(f"{file.filename}: Desteklenmeyen format. (PDF, DOCX, TXT gönderin)")
            
    return {
        "message": f"{processed_count} dosya başarıyla işlendi.",
        "errors": errors
    }

@app.post("/ask")
async def ask_question(request: QueryRequest):
    """
    Soru Sorma Endpoint'i:
    - Kullanıcı sorusunu alır.
    - Önce yerel dokümanlarda arama yapar.
    - Bulunamazsa Web'de (DuckDuckGo) arama yapar.
    - Gemini ile cevap üretir.
    """
    try:
        if not request.question:
            raise HTTPException(status_code=400, detail="Soru boş olamaz.")
            
        result = await process_query(request.question)
        return result
    except Exception as e:
        print(f"Sorgu Hatası: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files/list", response_model=List[str])
async def list_files():
    """İndekslenmiş dosyaların listesini döndürür."""
    return vector_store.list_files()

@app.delete("/files/clear")
async def clear_files():
    """
    Tüm veritabanını temizler.
    - İndeks dosyasını siler/sıfırlar.
    """
    try:
        # VectorStore'a clear metodu eklememiz gerekebilir veya dosyaları silip yeniden başlatabiliriz.
        # Şimdilik basitçe dosyaları silip servisi restart etmeyi öneren bir işlem yapalım veya
        # VectorStore class'ına reset metodu ekleyelim.
        # Hızlı çözüm:
        global vector_store 
        # (Bu mimaride singleton import edildiği için class üzerinde işlem yapmalıyız)
        # VectorStore'a reset metodu ekleyelim.
        if hasattr(vector_store, 'reset'):
            vector_store.reset()
        else:
            # Fallback: Dosyaları sil
            if os.path.exists("faiss_index.bin"): os.remove("faiss_index.bin")
            if os.path.exists("metadata.pkl"): os.remove("metadata.pkl")
            # Belleği de temizle (basitçe yeniden init ama singleton sorunu olabilir, restart en iyisi)
            return {"message": "İndeks dosyaları silindi. Lütfen servisi yeniden başlatın tam temizlik için."}
            
        return {"message": "Veritabanı başarıyla temizlendi."}
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
