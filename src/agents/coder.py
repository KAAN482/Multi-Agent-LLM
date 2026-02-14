"""
Coder (Kodlayıcı) ajan modülü.

Kod yazma ve çalıştırma tool'unu kullanarak hesaplama yapar.
Gemini 2.5 Flash modeli kullanır (güçlü kodlama yeteneği gerektirir).
"""

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from src.tools.code_executor import code_executor_tool
from src.monitoring.logger import get_logger

logger = get_logger(__name__)

# Coder sistem prompt'u
# Modelin bir Python geliştiricisi gibi davranmasını sağlar.
CODER_SYSTEM_PROMPT = """Sen bir kodlayıcı ajansın (Coder).

Görevin:
1. Verilen problemi analiz et
2. Çözmek için Python kodu yaz
3. code_executor_tool ile kodu çalıştır
4. Sonucu kontrol et ve raporla

Kurallar:
- Sadece Python kodu yaz
- Her zaman print() ile sonuçları yazdır (çıktının görünmesi için)
- Güvenli kod yaz (dosya işlemi, internet erişimi yapma)
- Kodun açık ve anlaşılır olmasına dikkat et
- Hata olursa düzeltip tekrar dene (en fazla 3 deneme)
- Karmaşık problemleri adımlara böl
- Türkçe açıklama yap ama kod İngilizce yazılabilir
"""


def create_coder_agent(llm):
    """
    Kodlayıcı ajan oluşturur.

    Kod çalıştırma tool'una erişimi olan bir LangChain agent oluşturur.

    Args:
        llm: LangChain uyumlu LLM nesnesi.

    Returns:
        Çağrılabilir agent nesnesi.
    """
    from langchain.agents import create_tool_calling_agent, AgentExecutor

    prompt = ChatPromptTemplate.from_messages([
        ("system", CODER_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    tools = [code_executor_tool]

    agent = create_tool_calling_agent(llm, tools, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5,
        handle_parsing_errors=True,
    )

    logger.info("Coder agent oluşturuldu")
    return executor


def run_coder(llm, query: str, messages: list = None) -> str:
    """
    Kodlayıcı ajanı çalıştırır.

    Tool binding desteklemeyen modeller için fallback olarak
    LLM'den kod üretip doğrudan çalıştırır.

    Args:
        llm: LangChain uyumlu LLM nesnesi.
        query: Çözülecek problem/görev.
        messages: Önceki mesaj geçmişi.

    Returns:
        str: Kod çalıştırma sonuçları.
    """
    logger.info("Coder çalıştırılıyor", extra={"query": query})

    try:
        # 1. Yöntem: Tool Calling Agent
        # Model kendisi kodu yazar ve executor tool'unu çağırır.
        executor = create_coder_agent(llm)
        result = executor.invoke({
            "input": query,
            "messages": messages or [],
        })
        return result.get("output", "Kod çalıştırma sonucu alınamadı.")

    except Exception as e:
        logger.warning(
            "Tool calling agent başarısız, fallback yönteme geçiliyor",
            extra={"error": str(e)},
        )

        # 2. Yöntem (Fallback): Kod Üret -> Çalıştır
        # Eğer ajan yapısı başarısız olursa, manuel olarak kod ürettirip çalıştırıyoruz.
        try:
            logger.info("Fallback: Manuel kod üretimi ve çalıştırma")
            
            # Sadece kod üretmeye odaklı basit prompt
            code_prompt = ChatPromptTemplate.from_messages([
                ("system", (
                    "Sen bir Python kod üreticisisin. "
                    "Verilen görevi çözen SADECE Python kodunu yaz. "
                    "Açıklama yazma, yalnızca çalıştırılabilir Python kodu üret. "
                    "Sonuçları her zaman print() ile yazdır."
                )),
                ("human", query),
            ])

            chain = code_prompt | llm
            result = chain.invoke({})
            code = result.content

            # Markdown kod bloklarını temizle (```python ... ```)
            if "```python" in code:
                code = code.split("```python")[1].split("```")[0].strip()
            elif "```" in code:
                code = code.split("```")[1].split("```")[0].strip()

            # Kodu çalıştır
            execution_result = code_executor_tool.invoke({"code": code})
            
            return f"Üretilen Kod:\n```python\n{code}\n```\n\n{execution_result}"

        except Exception as fallback_error:
            logger.error(
                "Coder tamamen başarısız",
                extra={"error": str(fallback_error)},
            )
            return f"Kod çalıştırma sırasında hata oluştu: {str(fallback_error)}"
