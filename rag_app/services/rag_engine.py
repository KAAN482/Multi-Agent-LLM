import os
import shutil
from langchain_google_genai import ChatGoogleGenerativeAI
from rag_app.services.embedding_service import embedding_service
from rag_app.services.vector_store import vector_store
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.3
)

SIMILARITY_THRESHOLD = 0.75  # E5 için benzerlik eşiği

async def process_query(question: str):
    try:
        # 1. Embedding oluştur
        print(f"Sorgu işleniyor: {question}")
        query_vec = embedding_service.embed_query(question)
        
        # 2. Vektör Araması (Retrieve)
        results = vector_store.search(query_vec, k=3)
        
        # Skor loglama
        print(f"Bulunan Doküman Sayısı: {len(results)}")
        for r in results:
            print(f" - {r['filename']} (Skor: {r['score']:.4f})")
        
        # 3. Sonuçları Değerlendir
        relevant_docs = [r for r in results if r['score'] > SIMILARITY_THRESHOLD]
    except Exception as e:
        print(f"Retrieval/Embedding hatası: {e}")
        relevant_docs = []

    sources = []
    context = ""
    
    if relevant_docs:
        print("Yeterli benzerlikte doküman bulundu.")
        # Doküman bulundu -> context oluştur
        context = "\n\n".join([f"Dosya: {d['filename']}\nİçerik: {d['text']}" for d in relevant_docs])
        sources = [d['filename'] for d in relevant_docs]
        
        prompt = f"""Aşağıdaki bağlamı kullanarak kullanıcı sorusunu cevapla. Sadece verilen bağlamdaki bilgileri kullan.
        
        Bağlam:
        {context}
        
        Soru: {question}
        
        Cevap:"""
         
        
    else:
        # Doküman bulunamadı -> Web Search (Fallback)
        print("Yeterli benzerlikte doküman YOK. Web aramasına gidiliyor...")
        try:
            from duckduckgo_search import DDGS
            with DDGS() as ddgs:
                # backend="html" daha dayanıklı
                results = list(ddgs.text(question, max_results=3, backend="html"))
                if results:
                    search_context = "\n".join([f"{r['title']}: {r['body']}" for r in results])
                    context = search_context
                    sources = ["Web Search (DuckDuckGo)"]
                    print("Web arama sonuçları bulundu.")
                else:
                    print("Web aramasından sonuç dönmedi.")
                    return {"answer": "Dokümanlarda bilgi yok ve web araması sonuç vermedi.", "sources": []}

            prompt = f"""Aşağıdaki arama sonuçlarını kullanarak kullanıcı sorusunu cevapla.
            
            Arama Sonuçları:
            {context}
            
            Soru: {question}
            
            Cevap:"""
        except Exception as e:
            print(f"Web arama hatası: {e}")
            return {"answer": "Üzgünüm, dokümanlarda bilgi bulamadım ve web araması başarısız oldu.", "sources": []}

    # 4. Gemini'ye sor (Generate)
    try:
        response = await llm.ainvoke(prompt)
        return {
            "answer": response.content,
            "sources": sources,
            "context_used": bool(relevant_docs)
        }
    except Exception as e:
        print(f"Gemini hatası: {e}")
        return {"answer": "Model yanıtı üretirken bir hata oluştu.", "sources": sources}
