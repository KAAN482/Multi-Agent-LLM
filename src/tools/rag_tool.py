from langchain_core.tools import tool
from src.utils.logger import get_logger
from rag_app.services.rag_engine import process_query

logger = get_logger(__name__)

@tool
async def rag_tool(query: str) -> str:
    """
    RAG sistemi üzerinden dokümanlarda arama yapar.
    
    Yerel dokümanlar (PDF, DOCX, TXT) üzerinde semantik arama yapar.
    Eğer dokümanlarda bilgi yoksa web aramasına (DuckDuckGo) düşebilir.
    
    Args:
        query: Kullanıcı sorusu veya aranacak konu.
        
    Returns:
        str: RAG sisteminin cevabı.
    """
    logger.info("RAG tool çağrıldı", extra={"query": query})
    try:
        # rag_engine.process_query bir dict döner: {"answer": ..., "sources": ...}
        result = await process_query(query)
        
        answer = result.get("answer", "Cevap üretilemedi.")
        sources = result.get("sources", [])
        
        formatted_response = f"{answer}\n\nKaynaklar: {', '.join(sources)}"
        return formatted_response
    except Exception as e:
        logger.error("RAG tool hatası", extra={"error": str(e)})
        return f"RAG Hatası: {str(e)}"
