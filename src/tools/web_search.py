"""
Web arama tool modülü.

DuckDuckGo arama motorunu kullanarak ücretsiz web araması yapar.
API key gerektirmez. LangChain tool olarak entegre edilir.
"""

from langchain_core.tools import tool
from src.utils.logger import get_logger

logger = get_logger(__name__)


# duckduckgo-search kütüphanesinin yüklü olup olmadığını kontrol et
try:
    from duckduckgo_search import DDGS
except ImportError:
    DDGS = None


@tool
def web_search_tool(query: str, max_results: int = 5) -> str:
    """
    DuckDuckGo üzerinden web araması yapar ve sonuçları döndürür.

    İnternet üzerinde arama yaparak güncel bilgilere erişir.
    Araştırma, doğrulama ve bilgi toplama görevlerinde kullanılır.

    Args:
        query: Aranacak sorgu metni.
        max_results: Döndürülecek maksimum sonuç sayısı (varsayılan: 5).

    Returns:
        str: Arama sonuçlarının formatlanmış metni.
    """
    # 1. Başlangıç Logu
    logger.info(
        "Web araması başlatılıyor",
        extra={"query": query, "max_results": max_results},
    )

    # 2. Kütüphane Kontrolü
    if DDGS is None:
        error_msg = (
            "duckduckgo-search kütüphanesi yüklü değil. "
            "Kurulum: pip install duckduckgo-search"
        )
        logger.error(error_msg)
        return f"Hata: {error_msg}"

    try:
        # 3. Arama İşlemi
        # DDGS nesnesi oluştur ve arama yap
        with DDGS() as ddgs:
            # .text() metodu güncel sürümlerde generator döndürür
            # Listeye çevirerek tüketiyoruz
            search_results = list(ddgs.text(query, max_results=max_results))

        results = []
        
        # 4. Sonuçları Formatla
        for result in search_results:
            results.append(
                f"**{result.get('title', 'Başlıksız')}**\n"
                f"Kaynak: {result.get('href', 'Bilinmiyor')}\n"
                f"Özet: {result.get('body', 'Özet yok')}\n"
            )

        # 5. Boş Sonuç Kontrolü
        if not results:
            logger.warning("Arama sonucu bulunamadı", extra={"query": query})
            return f"'{query}' için arama sonucu bulunamadı."

        # 6. Sonuçların Birleştirilmesi
        formatted_results = "\n---\n".join(results)
        
        logger.info(
            "Web araması tamamlandı",
            extra={"query": query, "result_count": len(results)},
        )
        return f"## Arama Sonuçları: '{query}'\n\n{formatted_results}"

    except Exception as e:
        # Beklenmeyen hata durumunda
        error_msg = f"Web araması sırasında hata oluştu: {str(e)}"
        logger.error(error_msg, extra={"query": query, "error": str(e)})
        return f"Hata: {error_msg}"
