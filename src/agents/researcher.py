"""
Researcher (Araştırmacı) ajan modülü.

Web arama tool'unu kullanarak internet araştırması yapar.
Gemini 2.5 Flash modeli kullanır (büyük context window ile
uzun metinleri okuyup özetleme yeteneği gerektirir).
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.tools.web_search import web_search_tool
from src.monitoring.logger import get_logger

logger = get_logger(__name__)

# Researcher sistem prompt'u
# Ajanın arama yapma ve bilgiyi sentezleme rolünü tanımlar.
RESEARCHER_SYSTEM_PROMPT = """Sen bir araştırmacı ajansın (Researcher).

Görevin:
1. Verilen sorgu hakkında web araması yap
2. Arama sonuçlarını oku ve ilgili bilgileri çıkar
3. Bilgileri kaynaklarıyla birlikte özetle

Kurallar:
- Her zaman web_search_tool'u kullanarak güncel bilgi topla
- Birden fazla arama yapabilirsin (farklı anahtar kelimelerle)
- Kaynak URL'lerini her zaman belirt
- Bilginin güvenilirliğini değerlendir
- Bulamadığın bilgiyi uydurma, "bu konuda bilgi bulunamadı" de
- Türkçe yanıtla
"""


def create_researcher_agent(llm):
    """
    Araştırmacı ajan oluşturur.

    Web arama tool'una erişimi olan bir LangChain agent oluşturur.
    Bu agent, tool calling (araç çağırma) yeteneğine sahiptir.

    Args:
        llm: LangChain uyumlu LLM nesnesi.

    Returns:
        Çağrılabilir agent nesnesi (AgentExecutor).
    """
    from langchain.agents import create_tool_calling_agent, AgentExecutor

    # Ajan prompt şablonu
    prompt = ChatPromptTemplate.from_messages([
        ("system", RESEARCHER_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"), # Tool çağrıları için gerekli
    ])

    # Ajanın kullanabileceği araçlar listesi
    tools = [web_search_tool]

    # Tool calling agent oluşturma
    agent = create_tool_calling_agent(llm, tools, prompt)
    
    # AgentExecutor ile sarmalama (hata yönetimi ve döngü kontrolü için)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,           # Sonsuz döngü koruması
        handle_parsing_errors=True, # Çıktı parse hatalarını yönet
    )

    logger.info("Researcher agent oluşturuldu")
    return executor


def run_researcher(llm, query: str, messages: list = None) -> str:
    """
    Araştırmacı ajanı çalıştırır.

    Tool binding desteklemeyen modeller veya beklenmedik hatalar için
    fallback (yedek) mekanizması içerir.

    Args:
        llm: LangChain uyumlu LLM nesnesi.
        query: Araştırılacak sorgu.
        messages: Önceki mesaj geçmişi.

    Returns:
        str: Araştırma sonuçları.
    """
    logger.info("Researcher çalıştırılıyor", extra={"query": query})

    try:
        # 1. Yöntem: Tool Calling Agent
        # Standart ve en yetenekli yöntem. Model kendisi tool çağırmaya karar verir.
        executor = create_researcher_agent(llm)
        result = executor.invoke({
            "input": query,
            "messages": messages or [],
        })
        return result.get("output", "Araştırma sonucu alınamadı.")

    except Exception as e:
        logger.warning(
            "Tool calling agent başarısız, fallback yönteme geçiliyor",
            extra={"error": str(e)},
        )

        # 2. Yöntem (Fallback): Manuel Arama + Özetleme
        # Eğer ajan oluşturma veya tool calling başarısız olursa,
        # aracı biz manuel çağırıp sonucu LLM'e özetletiyoruz.
        try:
            logger.info("Fallback: Manuel web araması yapılıyor")
            # Tool'u doğrudan çağır
            search_results = web_search_tool.invoke({"query": query})

            # LLM'e özetlet
            summarize_prompt = ChatPromptTemplate.from_messages([
                ("system", RESEARCHER_SYSTEM_PROMPT),
                (
                    "human",
                    f"Şu sorgu için web araması yapıldı: '{query}'\n\n"
                    f"Arama sonuçları:\n{search_results}\n\n"
                    "Bu sonuçları özetle ve kullanıcıya faydalı bilgiler sun."
                ),
            ])

            chain = summarize_prompt | llm
            result = chain.invoke({})
            return result.content

        except Exception as fallback_error:
            # Her iki yöntem de başarısız olursa
            logger.error(
                "Researcher tamamen başarısız",
                extra={"error": str(fallback_error)},
            )
            return f"Araştırma sırasında hata oluştu: {str(fallback_error)}"
