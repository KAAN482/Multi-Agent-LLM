"""
Konfigürasyon modülü.

Ortam değişkenlerini ve proje sabitlerini yönetir.
.env dosyasından API anahtarları ve ayarları yükler.
"""

import os
from dotenv import load_dotenv

# .env dosyasını yükle
load_dotenv()


# ─── Gemini (Bulut) Konfigürasyonu ───────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL_NAME = "gemini-2.5-flash"
GEMINI_TEMPERATURE = 0.7
GEMINI_MAX_TOKENS = 4096

# ─── Ollama (Yerel) Konfigürasyonu ──────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL", "llama3.2:3b")
OLLAMA_TEMPERATURE = 0.3
OLLAMA_MAX_TOKENS = 2048

# ─── LangFuse (Monitoring) Konfigürasyonu ───────────────────────────────────
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY", "")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY", "")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "http://localhost:3000")

# ─── Genel Ayarlar ──────────────────────────────────────────────────────────
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# ─── Model Seçim Eşik Değerleri ─────────────────────────────────────────────
# Metin uzunluğu bu değeri aşarsa "karmaşık" kabul edilir
COMPLEXITY_THRESHOLD_CHARS = 500
# Basit görev tipleri (yerel modele yönlendirilir)
SIMPLE_TASK_TYPES = ["greeting", "formatting", "review", "simple_qa"]
# Karmaşık görev tipleri (bulut modele yönlendirilir)
COMPLEX_TASK_TYPES = ["research", "coding", "analysis", "planning", "summarization"]

# ─── Kod Çalıştırıcı Güvenlik Ayarları ──────────────────────────────────────
CODE_EXECUTION_TIMEOUT = 10  # saniye
BLOCKED_MODULES = [
    "os", "subprocess", "sys", "shutil", "pathlib",
    "socket", "http", "urllib", "requests", "ctypes",
    "__import__", "eval", "exec", "compile", "open",
]
