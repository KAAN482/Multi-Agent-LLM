"""
Konfigürasyon modülü.

Ortam değişkenlerini ve proje sabitlerini yönetir.
.env dosyasından API anahtarları ve ayarları yükler.
Merkezi konfigürasyon noktasıdır.
"""

import os
from dotenv import load_dotenv

# .env dosyasını yükle (Varsa ortam değişkenlerini set eder)
load_dotenv()


# ─── Gemini (Bulut) Konfigürasyonu ───────────────────────────────────────────
# Google Gemini API anahtarı. Almak için: https://aistudio.google.com/app/apikey
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = "gemini-2.5-flash"
GEMINI_TEMPERATURE = 0.7  # Dengeli yaratıcılık
GEMINI_MAX_TOKENS = 4096  # Uzun yanıtlar için yeterli alan

# ─── Ollama (Yerel) Konfigürasyonu ──────────────────────────────────────────
# Yerel Ollama sunucusu adresi
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
# Kullanılacak yerel model (performans için küçük model seçildi)
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_TEMPERATURE = 0.3  # Daha tutarlı, daha az halüsinasyon
OLLAMA_MAX_TOKENS = 2048

# ─── LangFuse (Monitoring) Konfigürasyonu ───────────────────────────────────
# Opsiyonel: İzleme ve trace yönetimi için
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

# ─── Genel Ayarlar ──────────────────────────────────────────────────────────
# Log dosyalarının kaydedileceği dizin
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
# Log seviyesi (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ─── Model Seçim Eşik Değerleri ─────────────────────────────────────────────
# Metin uzunluğu bu değeri aşarsa görev "karmaşık" kabul edilir ve Gemini'ye gider
COMPLEXITY_THRESHOLD_CHARS = 500

# Basit görev tipleri (yerel modele yönlendirilir - Hız ve Maliyet tasarrufu)
SIMPLE_TASK_TYPES = ["greeting", "formatting", "review", "simple_qa"]

# Karmaşık görev tipleri (bulut modele yönlendirilir - Yüksek zeka gerektirir)
COMPLEX_TASK_TYPES = ["research", "coding", "analysis", "planning", "summarization"]

# ─── Kod Çalıştırıcı Güvenlik Ayarları ──────────────────────────────────────
CODE_EXECUTION_TIMEOUT = 10  # Kod en fazla 10 saniye çalışabilir (sonsuz döngü önlemi)

# Güvenlik amacıyla engellenen Python modülleri
BLOCKED_MODULES = [
    "os", "subprocess", "sys", "shutil", "pathlib",
    "socket", "http", "urllib", "requests", "ctypes",
    "__import__", "eval", "exec", "compile", "open",
]
