import os

# Kod Çalıştırma Ayarları
CODE_EXECUTION_TIMEOUT = 10  # Saniye
BLOCKED_MODULES = [
    "os", "subprocess", "sys", "shutil", 
    "pathlib", "socket", "http", "urllib", 
    "requests", "ctypes", "__import__", 
    "eval", "exec", "compile", "open"
]

# Model İsimleri (Sabitler)
MODEL_LLAMA_ANALYZER = "llama3.1:latest"        # RAG & Analiz
MODEL_DEEPSEEK_CODER = "deepseek-coder:1.3b"    # Mantık & Kod
MODEL_GEMINI_MASTER = "gemini-2.5-flash"        # Master & Web

# RAG Ayarları
SIMILARITY_THRESHOLD = 0.5
