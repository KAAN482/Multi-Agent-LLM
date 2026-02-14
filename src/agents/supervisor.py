"""
Supervisor (Yönetici) ajan modülü.

Kullanıcı sorgusunu analiz eder ve hangi ajana yönlendireceğine karar verir.
Gemini 2.5 Flash modeli kullanır (karmaşık karar verme gerektirir).
LangGraph state üzerinden diğer ajanları koordine eder.
"""

from src.monitoring.logger import get_logger

logger = get_logger(__name__)

# Supervisor sistem prompt'u
# Bu prompt, modelin bir yönlendirici (router) gibi davranmasını sağlar.
# Hangi görevin hangi ajana ait olduğunu tanımlar.
SUPERVISOR_SYSTEM_PROMPT = """Sen çok ajanlı bir sistemin yönetici ajanısın (Supervisor).

Görevin:
1. Kullanıcının sorgusunu analiz et
2. Sorguyu çözmek için hangi ajanların gerektiğine karar ver
3. Ajanları doğru sırayla yönlendir

Kullanılabilir ajanlar:
- researcher: İnternet araştırması yapar, güncel bilgi toplar
- coder: Python kodu yazar ve çalıştırır, hesaplama yapar
- reviewer: Sonuçları gözden geçirir, hata kontrolü yapar
- formatter: Sonuçları kullanıcıya sunmak için düzenler
- FINISH: Görev tamamlandı, son cevabı kullanıcıya sun

Karar verme kuralların:
- Bilgi gerektiren sorular → researcher
- Hesaplama/kod gerektiren sorular → coder
- Sonuçların doğrulanması gerekiyorsa → reviewer
- Son düzenleme ve sunum → formatter
- Her şey tamamsa → FINISH

Her seferinde yalnızca BİR sonraki ajan seçmelisin.
Yanıtını JSON formatında ver: {{"next": "ajan_adı", "reason": "kısa açıklama"}}
"""


def get_supervisor_prompt() -> str:
    """Supervisor sistem prompt'unu döndürür."""
    return SUPERVISOR_SYSTEM_PROMPT


def create_supervisor_chain(llm):
    """
    Supervisor karar zincirini oluşturur.

    LangChain prompt template ve LLM'i birleştirerek
    bir karar mekanizmasti (chain) oluşturur.

    Args:
        llm: LangChain uyumlu LLM nesnesi.

    Returns:
        Çağrılabilir chain nesnesi.
    """
    from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

    # Prompt şablonunu oluştur
    # System prompt + mesaj geçmişi + anlık durum bilgisi
    prompt = ChatPromptTemplate.from_messages([
        ("system", SUPERVISOR_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
        (
            "human",
            "Mevcut durum bilgisi:\n"
            "- Araştırma sonuçları: {search_results}\n"
            "- Kod sonuçları: {code_results}\n"
            "- İnceleme notları: {review_notes}\n\n"
            "Bir sonraki adım ne olmalı? JSON formatında yanıtla: "
            '{{\"next\": \"ajan_adı\", \"reason\": \"kısa açıklama\"}}'
        ),
    ])

    # Chain oluştur (Prompt -> LLM)
    chain = prompt | llm
    
    logger.info("Supervisor chain oluşturuldu")
    return chain
