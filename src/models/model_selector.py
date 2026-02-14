"""
Akıllı model seçim modülü.

Görev türüne, metin uzunluğuna ve hız/doğruluk dengesine göre
en uygun modeli (Gemini veya Ollama) otomatik olarak seçer.

Strateji:
- Karmaşık görevler (araştırma, kodlama, analiz) → Gemini 2.5 Flash (bulut)
- Basit görevler (selamlama, formatlama, gözden geçirme) → Llama 3.2 3B (yerel)
- Kullanıcı modu: "fast", "accurate", "auto"

Literatür Desteği:
- Küçük modeller basit görevlerde büyük modellerle benzer doğruluk sağlar
  (Schick et al., 2021 - "Toolformer")
- Hibrit yaklaşım maliyet/performans dengesini optimize eder
  (Chen et al., 2023 - "FrugalGPT")
"""

from typing import Literal
from langchain_core.language_models import BaseChatModel
from src.config import (
    COMPLEXITY_THRESHOLD_CHARS,
    SIMPLE_TASK_TYPES,
    COMPLEX_TASK_TYPES,
)
from src.models.gemini_model import get_gemini_model
from src.models.ollama_model import get_ollama_model, check_ollama_connection
from src.monitoring.logger import get_logger

logger = get_logger(__name__)

# Geçerli model seçim modları için tip tanımı
ModelMode = Literal["fast", "accurate", "auto"]


def classify_task(query: str) -> str:
    """
    Sorgu metnini analiz ederek görev türünü belirler.

    Basit anahtar kelime eşleştirmesi ile görev sınıflandırması yapar.
    Daha gelişmiş bir sınıflandırıcı ile değiştirilebilir (örn. Zero-shot classification).

    Args:
        query: Kullanıcının sorgu metni.

    Returns:
        str: Görev türü (research, coding, simple_qa, greeting, vb.)
    """
    # Sorguyu küçük harfe çevirerek eşleştirmeyi kolaylaştırıyoruz.
    query_lower = query.lower().strip()

    # 1. Selamlama Kontrolü
    # Basit konuşma başlatıcıları yerel modele yönlendirmek için tespit ediyoruz.
    greetings = ["merhaba", "selam", "hello", "hi", "hey", "nasılsın", "günaydın"]
    if any(query_lower.startswith(g) for g in greetings):
        return "greeting"

    # 2. Kodlama Görevi Kontrolü
    # Kod yazma isteği belirten anahtar kelimeleri arıyoruz.
    code_keywords = [
        "kod", "code", "python", "javascript", "hesapla", "calculate",
        "fonksiyon", "function", "algoritma", "program", "script",
        "fibonacci", "sırala", "sort", "döngü", "loop",
    ]
    if any(kw in query_lower for kw in code_keywords):
        return "coding"

    # 3. Araştırma Görevi Kontrolü
    # Bilgi arama veya analiz gerektiren kelimeleri arıyoruz.
    research_keywords = [
        "araştır", "research", "bul", "find", "nedir", "what is",
        "karşılaştır", "compare", "analiz", "analyze", "incele",
        "özetle", "summarize", "açıkla", "explain", "listele",
    ]
    if any(kw in query_lower for kw in research_keywords):
        return "research"

    # 4. Formatlama/Düzenleme Görevi Kontrolü
    # Metin düzenleme işlerini tespit ediyoruz.
    format_keywords = [
        "formatla", "format", "düzenle", "edit", "listele", "list",
        "tablo", "table", "madde", "bullet",
    ]
    if any(kw in query_lower for kw in format_keywords):
        return "formatting"

    # 5. Uzunluk Kontrolü
    # Eğer sorgu çok uzunsa (eşik değerinden fazla), bunu karmaşık bir analiz görevi sayıyoruz.
    if len(query) > COMPLEXITY_THRESHOLD_CHARS:
        return "analysis"

    # Varsayılan: Hiçbir kategoriye girmezse basit soru-cevap olarak işaretliyoruz.
    return "simple_qa"


def select_model(
    query: str,
    mode: ModelMode = "auto",
    task_type: str = None,
) -> tuple[BaseChatModel, str, str]:
    """
    Görev türüne ve moda göre en uygun modeli seçer.

    Args:
        query: Kullanıcının sorgu metni.
        mode: Seçim modu ("fast", "accurate", "auto").
        task_type: Önceden belirlenmiş görev türü (None ise otomatik algılanır).

    Returns:
        tuple: (model_nesnesi, model_adi, gorev_turu)

    Raises:
        ValueError: Geçersiz mod parametresi verilirse.
    """
    valid_modes = ("fast", "accurate", "auto")
    if mode not in valid_modes:
        raise ValueError(
            f"Geçersiz model seçim modu: '{mode}'. "
            f"Geçerli modlar: {valid_modes}"
        )

    # 1. Görev Türünü Belirleme
    # Eğer dışarıdan bir görev türü verilmediyse, classify_task ile biz belirliyoruz.
    if task_type is None:
        task_type = classify_task(query)

    # Seçim bağlamını logluyoruz (monitoring için önemli)
    logger.info(
        "Model seçimi yapılıyor",
        extra={
            "mode": mode,
            "task_type": task_type,
            "query_length": len(query),
        },
    )

    # 2. Mod Bazlı Seçim Mantığı

    # -- Fast (Hız) Modu --
    # Kullanıcı hızı önceliklendirdiyse, mümkünse yerel Ollama modelini kullanıyoruz.
    # Ancak Ollama çalışmıyorsa mecburen Gemini'ye (bulut) geçiyoruz.
    if mode == "fast":
        model, model_name = _try_ollama_first()
        logger.info(
            "Model seçildi (hız modu)",
            extra={"model": model_name, "task_type": task_type},
        )
        return model, model_name, task_type

    # -- Accurate (Doğruluk) Modu --
    # Kullanıcı doğruluğu önceliklendirdiyse, her zaman daha yetenekli olan Gemini modelini seçiyoruz.
    if mode == "accurate":
        model = get_gemini_model()
        model_name = "gemini-2.5-flash"
        logger.info(
            "Model seçildi (doğruluk modu)",
            extra={"model": model_name, "task_type": task_type},
        )
        return model, model_name, task_type

    # -- Auto (Otomatik) Mod --
    # Varsayılan mod. Görev türüne göre en mantıklı kararı veriyoruz.
    
    # Basit görevler -> Yerel Model (Ollama)
    if task_type in SIMPLE_TASK_TYPES:
        model, model_name = _try_ollama_first()
        
    # Karmaşık görevler -> Bulut Model (Gemini)
    elif task_type in COMPLEX_TASK_TYPES:
        model = get_gemini_model()
        model_name = "gemini-2.5-flash"
        
    else:
        # Bilinmeyen bir görev türüyle karşılaşırsak, güvenli tarafta kalıp güçlü modeli seçiyoruz.
        model = get_gemini_model()
        model_name = "gemini-2.5-flash"

    logger.info(
        "Model seçildi (otomatik mod)",
        extra={"model": model_name, "task_type": task_type},
    )
    return model, model_name, task_type


def _try_ollama_first() -> tuple[BaseChatModel, str]:
    """
    Önce Ollama'yı dener, bağlantı yoksa Gemini'ye fallback yapar.

    Returns:
        tuple: (model_nesnesi, model_adi)
    """
    # Ollama bağlantısını kontrol et
    if check_ollama_connection():
        try:
            # Bağlantı varsa modeli oluştur
            model = get_ollama_model()
            return model, "llama3.2:3b"
        except Exception as e:
            # Beklenmedik bir hata olursa uyarı ver ve Gemini'ye geç
            logger.warning(
                "Ollama başlatılamadı, Gemini'ye geçiliyor",
                extra={"error": str(e)},
            )

    # Ollama yoksa veya hata verdiyse Gemini'yi kullan
    logger.info("Ollama kullanılamıyor, Gemini modeli seçildi (fallback)")
    model = get_gemini_model()
    return model, "gemini-2.5-flash"
