from src.models.gemini_model import GeminiModel
from src.models.ollama_model import OllamaModel

class ModelSelector:
    """
    Görev türüne ve karmaşıklığına göre model seçen router sınıfı.
    """
    def __init__(self):
        self.fast_model = OllamaModel(temperature=0.3) # Llama 3.2
        self.smart_model = GeminiModel(temperature=0.7) # Gemini 2.5 Flash

    def select_model(self, task_type: str, complexity: str = "medium"):
        """
        Modele karar verir.
        task_type: 'coding', 'reasoning', 'chat', 'summary'
        complexity: 'low', 'medium', 'high'
        """
        # Kodlama veya yüksek karmaşıklık -> Gemini
        if task_type in ["coding", "reasoning"] or complexity == "high":
            return self.smart_model
            
        # Basit sohbet veya özetleme -> Llama (Hız ve Maliyet)
        if task_type in ["chat", "summary"] and complexity == "low":
            try:
                # Ollama'nın çalışıp çalışmadığını kontrol etmek iyi olurdu ama şimdilik varsayıyoruz.
                return self.fast_model
            except:
                return self.smart_model # Fallback
        
        # Varsayılan
        return self.smart_model
