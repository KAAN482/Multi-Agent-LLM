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
        query: Kullanıcının orijinal sorgusu. Değişmez.
        task_type: Classifier tarafından tespit edilen görev türü.
        messages: Mesaj geçmişi. LangGraph 'add_messages' reducer'ı ile listeye eklenir.
        search_results: Researcher ajanın bulduğu ham sonuçlar.
        code_results: Coder ajanın çalıştırdığı kod ve çıktısı.
        review_notes: Reviewer ajanın notları.
        review_status: İnceleme durumu (approved/needs_revision).
        final_answer: Formatter tarafından üretilen son cevap.
        next_agent: Supervisor tarafından belirlenen bir sonraki ajan.
        iteration_count: Döngü sayısı. Sonsuz döngüden kaçınmak için artırılır.
        model_used: Debug/Monitoring için kullanılan modellerin listesi.
        tools_called: Debug/Monitoring için çağrılan tool'ların listesi.
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
