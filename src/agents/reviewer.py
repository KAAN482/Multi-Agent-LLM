"""
Reviewer (Gözden Geçirici) ajan modülü.

Diğer ajanların çıktılarını gözden geçirir, kontrol eder.
Llama 3.2 3B (yerel/Ollama) modeli kullanır — basit kontrol
görevleri için yeterlidir ve API kotası harcamaz.
"""

from langchain_core.prompts import ChatPromptTemplate
from src.monitoring.logger import get_logger

logger = get_logger(__name__)

# Reviewer sistem prompt'u
# Kalite kontrol kriterlerini ve değerlendirme formatını tanımlar.
REVIEWER_SYSTEM_PROMPT = """Sen bir gözden geçirme ajanısın (Reviewer).

Görevin:
1. Diğer ajanların ürettiği sonuçları kontrol et
2. Doğruluk, tutarlılık ve kalite açısından değerlendir
3. Sorun varsa belirt, yoksa onayla

Kontrol maddelerin:
- Bilgi doğruluğu: Açıkça yanlış bilgi var mı?
- Tutarlılık: Cevap kendi içinde çelişiyor mu?
- Eksiksizlik: Soruya tam cevap verilmiş mi?
- Açıklık: Cevap anlaşılır mı?
- Kod kalitesi: Kod varsa, mantıklı ve doğru mu?

Yanıtını şu formatta ver:
- Durum: ONAY veya DÜZELTİ_GEREKLİ
- Notlar: Tespit ettiğin sorunlar veya iyileştirme önerileri
- Puan: 1-10 arası kalite puanı
"""


def run_reviewer(llm, content: str, original_query: str) -> dict:
    """
    Gözden geçirme ajanını çalıştırır.
    
    Verilen içeriği analiz eder ve yapılandırılmış bir değerlendirme döndürür.
    Tool kullanmaz, sadece LLM analizi yapar.

    Args:
        llm: LangChain uyumlu LLM nesnesi.
        content: Gözden geçirilecek içerik (araştırma/kod sonuçları).
        original_query: Orijinal kullanıcı sorusu.

    Returns:
        dict: {"status": "approved"/"needs_revision",
               "notes": "...",
               "score": int}
    """
    logger.info(
        "Reviewer çalıştırılıyor",
        extra={"content_length": len(content)},
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", REVIEWER_SYSTEM_PROMPT),
        (
            "human",
            f"Orijinal soru: {original_query}\n\n"
            f"Gözden geçirilecek içerik:\n{content}\n\n"
            "Bu içeriği kontrol et ve değerlendirmeni yap."
        ),
    ])

    try:
        # LLM zincirini çalıştır
        chain = prompt | llm
        result = chain.invoke({})
        review_text = result.content

        # Basit durum analizi
        # LLM çıktısında olumsuz anahtar kelimeler varsa revizyon iste
        status = "approved"
        negative_keywords = ["DÜZELTİ", "HATA", "YANLIŞ", "EKSİK", "NEEDS_REVISION", "GELİŞTİRİLMELİ"]
        if any(kw in review_text.upper() for kw in negative_keywords):
            status = "needs_revision"

        # Puan analizi
        # Metin içinden "Puan: 8" gibi bir ifadeyi regex ile çekmeye çalış
        score = 7  # Güvenli varsayılan
        import re
        score_match = re.search(r'[Pp]uan[:\s]*(\d+)', review_text)
        if score_match:
            score = min(10, max(1, int(score_match.group(1))))

        logger.info(
            "Review tamamlandı",
            extra={"status": status, "score": score},
        )

        return {
            "status": status,
            "notes": review_text,
            "score": score,
        }

    except Exception as e:
        logger.error(
            "Reviewer hatası",
            extra={"error": str(e)},
        )
        # Hata durumunda sistemi tıkamamak için otomatik onay veriyoruz,
        # ancak notlara hatayı ekliyoruz.
        return {
            "status": "approved",
            "notes": f"Review sırasında hata oluştu: {str(e)}. Otomatik onay verildi.",
            "score": 5,
        }
