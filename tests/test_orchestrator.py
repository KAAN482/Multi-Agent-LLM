"""
Orkestrasyon katmanı birim testleri.

LangGraph yapısını, routing mantığını
ve hata senaryolarını test eder.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.orchestrator.state import AgentState
from src.orchestrator.graph import (
    route_supervisor,
    run_multi_agent,
    MAX_ITERATIONS,
)


class TestAgentState:
    """AgentState yapısı testleri."""

    def test_state_has_required_fields(self):
        """AgentState gerekli alanları içerir."""
        required_fields = [
            "query", "task_type", "messages",
            "search_results", "code_results", "review_notes",
            "review_status", "final_answer", "next_agent",
            "iteration_count", "model_used", "tools_called",
        ]
        annotations = AgentState.__annotations__
        for field in required_fields:
            assert field in annotations, f"'{field}' alanı eksik"


class TestRouteSupervisor:
    """Supervisor routing fonksiyonu testleri."""

    def test_route_to_researcher(self):
        """Researcher'a doğru yönlendirir."""
        state = {"next_agent": "researcher", "final_answer": ""}
        assert route_supervisor(state) == "researcher"

    def test_route_to_coder(self):
        """Coder'a doğru yönlendirir."""
        state = {"next_agent": "coder", "final_answer": ""}
        assert route_supervisor(state) == "coder"

    def test_route_to_reviewer(self):
        """Reviewer'a doğru yönlendirir."""
        state = {"next_agent": "reviewer", "final_answer": ""}
        assert route_supervisor(state) == "reviewer"

    def test_route_to_formatter(self):
        """Formatter'a doğru yönlendirir."""
        state = {"next_agent": "formatter", "final_answer": ""}
        assert route_supervisor(state) == "formatter"

    def test_route_finish_with_answer(self):
        """FINISH ve cevap varsa END döner."""
        from langgraph.graph import END
        state = {"next_agent": "FINISH", "final_answer": "Some answer"}
        assert route_supervisor(state) == END

    def test_route_finish_without_answer(self):
        """FINISH ama cevap yoksa formatter'a yönlendirir."""
        state = {"next_agent": "FINISH", "final_answer": ""}
        assert route_supervisor(state) == "formatter"

    def test_route_default_finish(self):
        """next_agent boşsa FINISH gibi davranır."""
        state = {"final_answer": "answer"}
        # next_agent yoksa varsayılan FINISH
        from langgraph.graph import END
        assert route_supervisor(state) == END


class TestRunMultiAgent:
    """Çok ajanlı sistem çalıştırma testleri."""

    def test_empty_query_returns_error(self):
        """Boş sorgu hata mesajı döndürür."""
        result = run_multi_agent("")
        assert "Hata" in result["answer"] or "Boş" in result["answer"]
        assert result["iterations"] == 0

    def test_whitespace_query_returns_error(self):
        """Sadece boşluk sorgu hata döndürür."""
        result = run_multi_agent("   ")
        assert "Hata" in result["answer"] or "Boş" in result["answer"]

    def test_result_format(self):
        """Sonuç doğru formatta döner."""
        result = run_multi_agent("")
        assert "answer" in result
        assert "models_used" in result
        assert "tools_called" in result
        assert "iterations" in result
        assert isinstance(result["models_used"], list)
        assert isinstance(result["tools_called"], list)

    def test_max_iterations_constant(self):
        """Maksimum iterasyon sabiti tanımlı."""
        assert MAX_ITERATIONS > 0
        assert MAX_ITERATIONS <= 20  # Makul bir üst sınır
