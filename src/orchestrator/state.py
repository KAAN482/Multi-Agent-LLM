"""
Paylaşılan state tanımı modülü.

LangGraph'taki tüm ajanlar arasında paylaşılan
state (durum) yapısını tanımlar. TypedDict kullanarak
tip güvenliğini sağlar.
"""

from typing import Annotated, Sequence
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """
    Çok ajanlı sistemin paylaşılan durumu.

    Tüm ajanlar bu state üzerinden bilgi paylaşır.
    LangGraph, bu state'i otomatik olarak yönetir.

    Alanlar:
        query: Kullanıcının orijinal sorgusu.
        task_type: Otomatik tespit edilen görev türü.
        messages: Mesaj geçmişi (LangGraph tarafından birleştirilir).
        search_results: Araştırmacı ajanın bulduğu sonuçlar.
        code_results: Kodlayıcı ajanın çalıştırdığı kod sonuçları.
        review_notes: Gözden geçirici ajanın notları.
        review_status: İnceleme durumu (approved/needs_revision).
        final_answer: Formatlanmış son cevap.
        next_agent: Bir sonraki çalışacak ajan.
        iteration_count: Mevcut iterasyon sayısı (sonsuz döngü koruması).
        model_used: Kullanılan modellerin listesi.
        tools_called: Çağrılan tool'ların listesi.
    """
    query: str
    task_type: str
    messages: Annotated[Sequence[BaseMessage], add_messages]
    search_results: str
    code_results: str
    review_notes: str
    review_status: str
    final_answer: str
    next_agent: str
    iteration_count: int
    model_used: list[str]
    tools_called: list[str]
