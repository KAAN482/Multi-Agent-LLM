"""
Formatter (Formatlayıcı) ajan modülü.

Sonuçları kullanıcıya sunulmak üzere düzenler ve formatlar.
Llama 3.2 3B (yerel/Ollama) modeli kullanır — basit formatlama
görevleri için API kotası harcamaz ve hızlı çalışır.
"""

from langchain_core.prompts import ChatPromptTemplate
from src.monitoring.logger import get_logger

logger = get_logger(__name__)

# Formatter sistem prompt'u
# Çıktı formatını ve sunum kurallarını belirler.
FORMATTER_SYSTEM_PROMPT = """Sen bir formatlayıcı ajansın (Formatter).

Görevin:
1. Diğer ajanların ürettiği ham sonuçları al
2. Kullanıcıya sunulmak üzere düzenle ve formatla
3. Temiz, okunabilir ve profesyonel bir sunum oluştur

Formatlama kuralların:
- Markdown formatı kullan (başlıklar, listeler, kalın yazı)
- Gereksiz tekrarları kaldır
- Bilgileri mantıklı bir sıraya koy
- Kaynak varsa belirt
- Kod varsa kod bloğu içinde göster
- Sonucu Türkçe olarak sun
- Kısa ve öz ol, gereksiz uzatma
"""


def run_formatter(llm, content: str, original_query: str) -> str:
    """
    Formatlayıcı ajanı çalıştırır.

    Ham sonuçları kullanıcıya sunulacak düzgün formata çevirir.
    
    Args:
        llm: LangChain uyumlu LLM nesnesi.
        content: Formatlanacak ham içerik (tüm sonuçların birleşimi).
        original_query: Orijinal kullanıcı sorusu.

    Returns:
        str: Formatlanmış final cevap.
    """
    logger.info(
        "Formatter çalıştırılıyor",
        extra={"content_length": len(content)},
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", FORMATTER_SYSTEM_PROMPT),
        (
            "human",
            f"Kullanıcının sorusu: {original_query}\n\n"
            f"Ham sonuçlar:\n{content}\n\n"
            "Bu sonuçları düzenle ve kullanıcıya sunulmak üzere formatla."
        ),
    ])

    try:
        # LLM zincirini çalıştır
        chain = prompt | llm
        result = chain.invoke({})

        formatted = result.content
        logger.info(
            "Formatlama tamamlandı",
            extra={"output_length": len(formatted)},
        )
        return formatted

    except Exception as e:
        logger.error(
            "Formatter hatası",
            extra={"error": str(e)},
        )
        # Hata durumunda, kullanıcının en azından ham veriyi görebilmesi için
        # orijinal içeriği olduğu gibi döndür.
        return f"(Formatlama başarısız - ham sonuç)\n\n{content}"
