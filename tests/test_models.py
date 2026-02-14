"""
Model katmanı birim testleri.

Model seçim fonksiyonunu, görev sınıflandırmasını ve
hata senaryolarını test eder.
"""

import pytest
from unittest.mock import patch, MagicMock
from src.models.model_selector import classify_task, select_model


class TestClassifyTask:
    """Görev sınıflandırma fonksiyonu testleri."""

    def test_greeting_detection(self):
        """Selamlama mesajlarını doğru tespit eder."""
        assert classify_task("Merhaba") == "greeting"
        assert classify_task("selam nasılsın") == "greeting"
        assert classify_task("Hello there") == "greeting"

    def test_coding_detection(self):
        """Kodlama görevlerini doğru tespit eder."""
        assert classify_task("fibonacci hesapla") == "coding"
        assert classify_task("Python fonksiyonu yaz") == "coding"
        assert classify_task("bir sıralama algoritması oluştur") == "coding"

    def test_research_detection(self):
        """Araştırma görevlerini doğru tespit eder."""
        assert classify_task("yapay zeka nedir") == "research"
        assert classify_task("iki framework'ü karşılaştır") == "research"
        assert classify_task("bu konuyu araştır") == "research"

    def test_formatting_detection(self):
        """Formatlama görevlerini doğru tespit eder."""
        assert classify_task("bunu tablo halinde formatla") == "formatting"

    def test_long_text_is_analysis(self):
        """Uzun metinler analiz görevi olarak sınıflandırılır."""
        long_text = "a" * 600
        assert classify_task(long_text) == "analysis"

    def test_simple_qa_default(self):
        """Bilinmeyen kısa sorgular simple_qa olarak sınıflandırılır."""
        assert classify_task("bugün hava nasıl?") == "simple_qa"

    def test_empty_query(self):
        """Boş sorgu simple_qa döner."""
        assert classify_task("") == "simple_qa"


class TestSelectModel:
    """Model seçim fonksiyonu testleri."""

    def test_invalid_mode_raises_error(self):
        """Geçersiz mod parametresi ValueError fırlatır."""
        with pytest.raises(ValueError, match="Geçersiz model seçim modu"):
            select_model("test query", mode="invalid_mode")

    def test_invalid_mode_error_message(self):
        """Hata mesajı geçerli modları içerir."""
        with pytest.raises(ValueError) as exc_info:
            select_model("test", mode="turbo")
        assert "fast" in str(exc_info.value)
        assert "accurate" in str(exc_info.value)
        assert "auto" in str(exc_info.value)

    @patch("src.models.model_selector.get_gemini_model")
    def test_accurate_mode_uses_gemini(self, mock_gemini):
        """Doğruluk modu her zaman Gemini kullanır."""
        mock_model = MagicMock()
        mock_gemini.return_value = mock_model

        model, name, task = select_model("test", mode="accurate")
        assert name == "gemini-2.5-flash"
        mock_gemini.assert_called_once()

    @patch("src.models.model_selector.check_ollama_connection")
    @patch("src.models.model_selector.get_ollama_model")
    def test_fast_mode_tries_ollama(self, mock_ollama, mock_check):
        """Hız modu önce Ollama'yı dener."""
        mock_check.return_value = True
        mock_model = MagicMock()
        mock_ollama.return_value = mock_model

        model, name, task = select_model("test", mode="fast")
        assert name == "llama3.2:3b"

    @patch("src.models.model_selector.check_ollama_connection")
    @patch("src.models.model_selector.get_gemini_model")
    def test_fast_mode_fallback_to_gemini(self, mock_gemini, mock_check):
        """Ollama yoksa Gemini'ye düşer."""
        mock_check.return_value = False
        mock_model = MagicMock()
        mock_gemini.return_value = mock_model

        model, name, task = select_model("test", mode="fast")
        assert name == "gemini-2.5-flash"

    @patch("src.models.model_selector.get_gemini_model")
    def test_auto_mode_complex_task(self, mock_gemini):
        """Otomatik modda karmaşık görev Gemini seçer."""
        mock_model = MagicMock()
        mock_gemini.return_value = mock_model

        model, name, task = select_model(
            "Python kodu yaz",
            mode="auto",
            task_type="coding",
        )
        assert name == "gemini-2.5-flash"

    @patch("src.models.model_selector.check_ollama_connection")
    @patch("src.models.model_selector.get_ollama_model")
    def test_auto_mode_simple_task(self, mock_ollama, mock_check):
        """Otomatik modda basit görev Ollama seçer."""
        mock_check.return_value = True
        mock_model = MagicMock()
        mock_ollama.return_value = mock_model

        model, name, task = select_model(
            "merhaba",
            mode="auto",
            task_type="greeting",
        )
        assert name == "llama3.2:3b"

    def test_returns_three_values(self):
        """select_model her zaman 3 değer döndürür."""
        with patch("src.models.model_selector.get_gemini_model") as mock:
            mock.return_value = MagicMock()
            result = select_model("test", mode="accurate")
            assert len(result) == 3
            model, name, task_type = result
            assert isinstance(name, str)
            assert isinstance(task_type, str)
