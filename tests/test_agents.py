"""
Ajan katmanı birim testleri.

Her ajanın prompt yapısını, rol atamasını ve
hata durumlarını test eder.
"""

import pytest
from unittest.mock import patch, MagicMock
from langchain_core.messages import AIMessage


class TestSupervisorAgent:
    """Supervisor ajan testleri."""

    def test_prompt_contains_agent_names(self):
        """Supervisor prompt'u tüm ajan adlarını içerir."""
        from src.agents.supervisor import SUPERVISOR_SYSTEM_PROMPT

        assert "researcher" in SUPERVISOR_SYSTEM_PROMPT
        assert "coder" in SUPERVISOR_SYSTEM_PROMPT
        assert "reviewer" in SUPERVISOR_SYSTEM_PROMPT
        assert "formatter" in SUPERVISOR_SYSTEM_PROMPT
        assert "FINISH" in SUPERVISOR_SYSTEM_PROMPT

    def test_prompt_defines_role(self):
        """Supervisor prompt'u rol tanımı içerir."""
        from src.agents.supervisor import SUPERVISOR_SYSTEM_PROMPT

        assert "yönetici" in SUPERVISOR_SYSTEM_PROMPT.lower() or \
               "supervisor" in SUPERVISOR_SYSTEM_PROMPT.lower()

    def test_get_supervisor_prompt_returns_string(self):
        """get_supervisor_prompt string döner."""
        from src.agents.supervisor import get_supervisor_prompt

        prompt = get_supervisor_prompt()
        assert isinstance(prompt, str)
        assert len(prompt) > 100

    def test_create_supervisor_chain(self):
        """Supervisor chain başarıyla oluşturulur."""
        from src.agents.supervisor import create_supervisor_chain

        mock_llm = MagicMock()
        mock_llm.__or__ = MagicMock(return_value=MagicMock())

        chain = create_supervisor_chain(mock_llm)
        assert chain is not None


class TestResearcherAgent:
    """Researcher ajan testleri."""

    def test_prompt_mentions_web_search(self):
        """Researcher prompt'u web aramasından bahseder."""
        from src.agents.researcher import RESEARCHER_SYSTEM_PROMPT

        assert "arama" in RESEARCHER_SYSTEM_PROMPT.lower() or \
               "search" in RESEARCHER_SYSTEM_PROMPT.lower()

    def test_prompt_mentions_sources(self):
        """Researcher prompt'u kaynak belirtmeyi zorunlu kılar."""
        from src.agents.researcher import RESEARCHER_SYSTEM_PROMPT

        assert "kaynak" in RESEARCHER_SYSTEM_PROMPT.lower() or \
               "url" in RESEARCHER_SYSTEM_PROMPT.lower()

    @patch("src.agents.researcher.web_search_tool")
    def test_run_researcher_error_handling(self, mock_search):
        """Researcher hata durumunda mesaj döndürür."""
        from src.agents.researcher import run_researcher

        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("Test error")
        mock_search.invoke.side_effect = Exception("Search failed")

        result = run_researcher(mock_llm, "test query")
        assert "hata" in result.lower() or "error" in result.lower()


class TestCoderAgent:
    """Coder ajan testleri."""

    def test_prompt_mentions_python(self):
        """Coder prompt'u Python'dan bahseder."""
        from src.agents.coder import CODER_SYSTEM_PROMPT

        assert "python" in CODER_SYSTEM_PROMPT.lower()

    def test_prompt_mentions_print(self):
        """Coder prompt'u print() kullanmayı belirtir."""
        from src.agents.coder import CODER_SYSTEM_PROMPT

        assert "print" in CODER_SYSTEM_PROMPT.lower()

    def test_prompt_mentions_safety(self):
        """Coder prompt'u güvenlik kurallarından bahseder."""
        from src.agents.coder import CODER_SYSTEM_PROMPT

        assert "güvenli" in CODER_SYSTEM_PROMPT.lower() or \
               "safe" in CODER_SYSTEM_PROMPT.lower()


class TestReviewerAgent:
    """Reviewer ajan testleri."""

    def test_prompt_has_checklist(self):
        """Reviewer prompt'u kontrol maddelerini içerir."""
        from src.agents.reviewer import REVIEWER_SYSTEM_PROMPT

        assert "doğruluk" in REVIEWER_SYSTEM_PROMPT.lower() or \
               "doğruluk" in REVIEWER_SYSTEM_PROMPT
        assert "tutarlılık" in REVIEWER_SYSTEM_PROMPT.lower() or \
               "tutarlılık" in REVIEWER_SYSTEM_PROMPT

    def test_run_reviewer_returns_dict(self):
        """run_reviewer sözlük döndürür."""
        from src.agents.reviewer import run_reviewer

        mock_llm = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Durum: ONAY\nNotlar: İyi görünüyor\nPuan: 8"
        mock_llm.invoke.return_value = mock_response

        # Chain mock
        with patch("src.agents.reviewer.ChatPromptTemplate") as mock_prompt:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = mock_response
            mock_prompt.from_messages.return_value.__or__ = MagicMock(
                return_value=mock_chain
            )

            result = run_reviewer(mock_llm, "test content", "test query")
            assert isinstance(result, dict)
            assert "status" in result
            assert "notes" in result
            assert "score" in result

    def test_run_reviewer_error_returns_approved(self):
        """Reviewer hata durumunda otomatik onay verir."""
        from src.agents.reviewer import run_reviewer

        mock_llm = MagicMock()
        mock_llm.invoke.side_effect = Exception("Model error")

        with patch("src.agents.reviewer.ChatPromptTemplate") as mock_prompt:
            mock_prompt.from_messages.return_value.__or__ = MagicMock(
                side_effect=Exception("Chain error")
            )

            result = run_reviewer(mock_llm, "test", "test")
            assert result["status"] == "approved"


class TestFormatterAgent:
    """Formatter ajan testleri."""

    def test_prompt_mentions_markdown(self):
        """Formatter prompt'u Markdown formatından bahseder."""
        from src.agents.formatter import FORMATTER_SYSTEM_PROMPT

        assert "markdown" in FORMATTER_SYSTEM_PROMPT.lower()

    def test_prompt_mentions_turkish(self):
        """Formatter prompt'u Türkçe'den bahseder."""
        from src.agents.formatter import FORMATTER_SYSTEM_PROMPT

        assert "türkçe" in FORMATTER_SYSTEM_PROMPT.lower()

    def test_run_formatter_error_returns_raw(self):
        """Formatter hata durumunda ham içeriği döndürür."""
        from src.agents.formatter import run_formatter

        mock_llm = MagicMock()

        with patch("src.agents.formatter.ChatPromptTemplate") as mock_prompt:
            mock_prompt.from_messages.return_value.__or__ = MagicMock(
                side_effect=Exception("Format error")
            )

            result = run_formatter(mock_llm, "raw content", "test query")
            assert "raw content" in result
