"""
LangGraph orkestrasyon modülü.

Tüm ajanları bir LangGraph StateGraph üzerinde koordine eder.
Supervisor'ın kararlarına göre ajanlar arası yönlendirme yapar.
Karmaşık iş akışını (workflow) tanımlar.
"""

import json
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from src.orchestrator.state import AgentState
from src.models.model_selector import select_model
from src.agents.supervisor import create_supervisor_chain
from src.agents.researcher import run_researcher
from src.agents.coder import run_coder
from src.agents.reviewer import run_reviewer
from src.agents.formatter import run_formatter
from src.monitoring.logger import get_logger

logger = get_logger(__name__)

# Sonsuz döngü koruması - maksimum iterasyon sayısı
# Bu sayıya ulaşılınca sistem zorla durdurulur (FINISH).
MAX_ITERATIONS = 10


# ─── Node Fonksiyonları ─────────────────────────────────────────────────────

def supervisor_node(state: AgentState) -> dict:
    """
    Supervisor düğümü: Bir sonraki ajanı belirler.

    Kullanıcı sorgusunu ve mevcut durumu analiz ederek
    hangi ajanın çalışması gerektiğine karar verir.
    """
    logger.info("Supervisor düğümü çalışıyor")

    # 1. Model Seçimi
    # Karar verme karmaşık bir işlem olduğu için "accurate" modunda (Gemini) çalıştırılır.
    model, model_name, _ = select_model(
        state["query"], mode="accurate", task_type="planning"
    )

    # 2. Zinciri Çalıştırma
    chain = create_supervisor_chain(model)
    result = chain.invoke({
        "messages": state["messages"],
        "search_results": state.get("search_results", "Henüz yok"),
        "code_results": state.get("code_results", "Henüz yok"),
        "review_notes": state.get("review_notes", "Henüz yok"),
    })

    response_text = result.content

    # 3. JSON Yanıtını Ayrıştırma
    # Modelin ürettiği metin içinden JSON bloğunu bulup parse ediyoruz.
    next_agent = "FINISH"
    try:
        json_start = response_text.find("{")
        json_end = response_text.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            parsed = json.loads(response_text[json_start:json_end])
            next_agent = parsed.get("next", "FINISH")
            reason = parsed.get("reason", "Belirtilmedi")
            logger.info(
                "Supervisor kararı",
                extra={"next_agent": next_agent, "reason": reason},
            )
    except json.JSONDecodeError:
        logger.warning(
            "Supervisor JSON parse hatası, varsayılan FINISH",
            extra={"response": response_text[:200]},
        )

    # 4. Geçerlilik Kontrolü
    # Model bazen var olmayan ajan isimleri uydurabilir, kontrol ediyoruz.
    valid_agents = {"researcher", "coder", "reviewer", "formatter", "FINISH"}
    if next_agent not in valid_agents:
        logger.warning(
            f"Geçersiz ajan adı: {next_agent}, FINISH olarak değiştiriliyor"
        )
        next_agent = "FINISH"

    # 5. Sonsuz Döngü Koruması
    iteration = state.get("iteration_count", 0) + 1
    if iteration >= MAX_ITERATIONS:
        logger.warning(
            f"Maksimum iterasyona ulaşıldı ({MAX_ITERATIONS}), FINISH"
        )
        next_agent = "FINISH"

    # İstatistikleri güncelle
    model_used = state.get("model_used", [])
    model_used.append(f"supervisor:{model_name}")

    return {
        "next_agent": next_agent,
        "iteration_count": iteration,
        "model_used": model_used,
        "messages": [AIMessage(content=f"Supervisor kararı: {next_agent}")],
    }


def researcher_node(state: AgentState) -> dict:
    """
    Researcher düğümü: Web araştırması yapar.

    DuckDuckGo ile internet araması yaparak bilgi toplar.
    Gemini modeli kullanır.
    """
    logger.info("Researcher düğümü çalışıyor")

    model, model_name, _ = select_model(
        state["query"], mode="accurate", task_type="research"
    )

    result = run_researcher(
        llm=model,
        query=state["query"],
        messages=list(state.get("messages", [])),
    )

    # İstatistikler
    model_used = state.get("model_used", [])
    model_used.append(f"researcher:{model_name}")

    tools_called = state.get("tools_called", [])
    tools_called.append("web_search")

    return {
        "search_results": result,
        "model_used": model_used,
        "tools_called": tools_called,
        "messages": [AIMessage(content=f"Araştırma sonuçları: {result[:500]}")],
    }


def coder_node(state: AgentState) -> dict:
    """
    Coder düğümü: Kod yazar ve çalıştırır.

    Python kodu üretir ve güvenli ortamda çalıştırır.
    Gemini modeli kullanır.
    """
    logger.info("Coder düğümü çalışıyor")

    model, model_name, _ = select_model(
        state["query"], mode="accurate", task_type="coding"
    )

    result = run_coder(
        llm=model,
        query=state["query"],
        messages=list(state.get("messages", [])),
    )

    model_used = state.get("model_used", [])
    model_used.append(f"coder:{model_name}")

    tools_called = state.get("tools_called", [])
    tools_called.append("code_executor")

    return {
        "code_results": result,
        "model_used": model_used,
        "tools_called": tools_called,
        "messages": [AIMessage(content=f"Kod sonuçları: {result[:500]}")],
    }


def reviewer_node(state: AgentState) -> dict:
    """
    Reviewer düğümü: Sonuçları gözden geçirir.

    Araştırma ve kod sonuçlarını kontrol eder.
    Llama 3.2 yerel modeli kullanır (basit kontrol görevi).
    """
    logger.info("Reviewer düğümü çalışıyor")

    model, model_name, _ = select_model(
        state["query"], mode="fast", task_type="review"
    )

    # Gözden geçirilecek içeriği topla
    content_parts = []
    if state.get("search_results"):
        content_parts.append(f"Araştırma:\n{state['search_results']}")
    if state.get("code_results"):
        content_parts.append(f"Kod Sonuçları:\n{state['code_results']}")

    content = "\n\n---\n\n".join(content_parts) if content_parts else "İçerik yok"

    review = run_reviewer(
        llm=model,
        content=content,
        original_query=state["query"],
    )

    model_used = state.get("model_used", [])
    model_used.append(f"reviewer:{model_name}")

    return {
        "review_notes": review["notes"],
        "review_status": review["status"],
        "model_used": model_used,
        "messages": [AIMessage(
            content=f"Review: {review['status']} (Puan: {review['score']})"
        )],
    }


def formatter_node(state: AgentState) -> dict:
    """
    Formatter düğümü: Sonuçları formatlar.

    Tüm sonuçları düzenleyerek kullanıcıya sunulacak
    final cevabı oluşturur.
    Llama 3.2 yerel modeli kullanır (basit formatlama görevi).
    """
    logger.info("Formatter düğümü çalışıyor")

    model, model_name, _ = select_model(
        state["query"], mode="fast", task_type="formatting"
    )

    # Formatlanacak içeriği topla (tüm bulgular + inceleme notları)
    content_parts = []
    if state.get("search_results"):
        content_parts.append(f"Araştırma Sonuçları:\n{state['search_results']}")
    if state.get("code_results"):
        content_parts.append(f"Kod Sonuçları:\n{state['code_results']}")
    if state.get("review_notes"):
        content_parts.append(f"İnceleme Notları:\n{state['review_notes']}")

    content = "\n\n---\n\n".join(content_parts) if content_parts else state["query"]

    formatted = run_formatter(
        llm=model,
        content=content,
        original_query=state["query"],
    )

    model_used = state.get("model_used", [])
    model_used.append(f"formatter:{model_name}")

    return {
        "final_answer": formatted,
        "model_used": model_used,
        "messages": [AIMessage(content=f"Final cevap hazırlandı")],
    }


# ─── Routing Fonksiyonu ─────────────────────────────────────────────────────

def route_supervisor(state: AgentState) -> str:
    """
    Supervisor'ın kararına göre sonraki düğümü belirler.

    Conditional Edge (Koşullu Kenar) olarak kullanılır.
    """
    next_agent = state.get("next_agent", "FINISH")

    if next_agent == "FINISH":
        # Eğer iş bitti denildiyse ama henüz formatlanmış cevap yoksa
        # Otomatik olarak formatter'a gönder
        if not state.get("final_answer"):
            return "formatter"
        return END

    return next_agent


# ─── Graph Oluşturma ────────────────────────────────────────────────────────

def create_graph() -> StateGraph:
    """
    Multi-agent LangGraph'ı oluşturur ve derler.

    Ajanlar arası iş akışını tanımlar:
    supervisor → (researcher|coder|formatter) → reviewer → supervisor → ...
    """
    logger.info("LangGraph oluşturuluyor")

    # 1. Workflow Başlatma
    workflow = StateGraph(AgentState)

    # 2. Düğümleri Ekleme
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("researcher", researcher_node)
    workflow.add_node("coder", coder_node)
    workflow.add_node("reviewer", reviewer_node)
    workflow.add_node("formatter", formatter_node)

    # 3. Giriş Noktası
    workflow.set_entry_point("supervisor")

    # 4. Yönlendirme Mantığı (Conditional Edges)
    # Supervisor'dan sonra nereye gidileceğini 'route_supervisor' fonksiyonu belirler
    workflow.add_conditional_edges(
        "supervisor",
        route_supervisor,
        {
            "researcher": "researcher",
            "coder": "coder",
            "reviewer": "reviewer",
            "formatter": "formatter",
            END: END,
        },
    )

    # 5. Geri Dönüşler
    # İş ajanları görevlerini bitirince tekrar Supervisor'a dönerler (Döngü)
    workflow.add_edge("researcher", "supervisor")
    workflow.add_edge("coder", "supervisor")
    workflow.add_edge("reviewer", "supervisor")
    workflow.add_edge("formatter", "supervisor")

    # 6. Derleme
    graph = workflow.compile()
    logger.info("LangGraph başarıyla oluşturuldu ve derlendi")

    return graph


def run_multi_agent(query: str, mode: str = "auto") -> dict:
    """
    Çok ajanlı sistemi çalıştırır.

    Kullanıcı sorgusunu alır, LangGraph'ı başlatır ve
    ajanları koordine ederek sonuç üretir.
    
    Tüm hata yönetimi ve istatistik toplama bu noktada yapılır.

    Args:
        query: Kullanıcının sorgusu.
        mode: Model seçim modu ("fast", "accurate", "auto").

    Returns:
        dict: {
            "answer": str,
            "models_used": list,
            "tools_called": list,
            "iterations": int,
        }
    """
    # Boş sorgu kontrolü
    if not query or not query.strip():
        return {
            "answer": "Hata: Boş sorgu gönderilemez. Lütfen bir soru sorun.",
            "models_used": [],
            "tools_called": [],
            "iterations": 0,
        }

    logger.info(
        "Çok ajanlı sistem başlatılıyor",
        extra={"query": query, "mode": mode},
    )

    # Graph Nesnesi
    graph = create_graph()

    # Başlangıç State'i
    initial_state = {
        "query": query,
        "task_type": "",
        "messages": [HumanMessage(content=query)],
        "search_results": "",
        "code_results": "",
        "review_notes": "",
        "review_status": "",
        "final_answer": "",
        "next_agent": "",
        "iteration_count": 0,
        "model_used": [],
        "tools_called": [],
    }

    try:
        # Graph Execution
        final_state = graph.invoke(initial_state)

        # Sonuç Hazırlama
        answer = final_state.get("final_answer", "")
        if not answer:
            # Final cevap yoksa mevcut parçaları topla (fallback)
            parts = []
            if final_state.get("search_results"):
                parts.append(final_state["search_results"])
            if final_state.get("code_results"):
                parts.append(final_state["code_results"])
            answer = "\n\n".join(parts) if parts else "Yanıt üretilemedi."

        result = {
            "answer": answer,
            "models_used": final_state.get("model_used", []),
            "tools_called": final_state.get("tools_called", []),
            "iterations": final_state.get("iteration_count", 0),
        }

        logger.info(
            "Çok ajanlı sistem tamamlandı",
            extra={
                "iterations": result["iterations"],
                "models_count": len(result["models_used"]),
                "tools_count": len(result["tools_called"]),
            },
        )

        return result

    except Exception as e:
        logger.error(
            "Çok ajanlı sistem hatası",
            extra={"error": str(e)},
            exc_info=True,
        )
        return {
            "answer": f"Sistem hatası oluştu: {str(e)}",
            "models_used": [],
            "tools_called": [],
            "iterations": 0,
        }
