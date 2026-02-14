"""
Loglama ve monitoring modülü.

JSON formatında yapılandırılmış loglama sağlar.
Her istek/yanıt, seçilen model, çağrılan tool ve hata kayıtlarını tutar.
Opsiyonel olarak LangFuse entegrasyonu destekler.
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Optional
from src.config import LOG_DIR, LOG_LEVEL


def _ensure_log_dir():
    """Log dizininin var olduğundan emin olur."""
    os.makedirs(LOG_DIR, exist_ok=True)


class JsonFormatter(logging.Formatter):
    """
    Log kayıtlarını JSON formatında biçimlendirir.

    Modern log yönetim sistemleri (ELK, Datadog, vb.) ve
    kolay debug için JSON formatı tercih edilir.

    Her log kaydı şu alanları içerir:
    - timestamp: ISO 8601 formatında zaman damgası
    - level: Log seviyesi (INFO, WARNING, ERROR vb.)
    - logger: Logger adı
    - message: Log mesajı
    - extra: Ek bilgiler (context)
    """

    def format(self, record: logging.LogRecord) -> str:
        """Log kaydını JSON string'e dönüştürür."""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Standart logging alanlarını çıkar, geri kalanları 'extra' olarak ekle
        standard_attrs = {
            "name", "msg", "args", "created", "relativeCreated",
            "exc_info", "exc_text", "stack_info", "lineno", "funcName",
            "pathname", "filename", "module", "levelno", "levelname",
            "msecs", "thread", "threadName", "process", "processName",
            "message", "taskName",
        }

        extra = {
            key: value
            for key, value in record.__dict__.items()
            if key not in standard_attrs
        }
        if extra:
            log_data["extra"] = extra

        # Exception bilgisi varsa yapılandırılmış olarak ekle
        if record.exc_info and record.exc_info[1]:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
            }

        return json.dumps(log_data, ensure_ascii=False, default=str)


def get_logger(name: str) -> logging.Logger:
    """
    İsimlendirilmiş bir logger oluşturur veya mevcut olanı döndürür.

    Çift hedefli (Dual-target) logging yapar:
    1. Konsol: İnsan tarafından okunabilir basit format.
    2. Dosya: Makine tarafından okunabilir JSON formatı.

    Args:
        name: Logger adı (genellikle modül adı __name__).

    Returns:
        logging.Logger: Yapılandırılmış logger nesnesi.
    """
    logger = logging.getLogger(name)

    # Logger zaten yapılandırılmışsa tekrar yapılandırma (Duplicate log önleme)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, LOG_LEVEL, logging.INFO))

    # 1. Konsol Handler (Okunabilir Format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # 2. Dosya Handler (JSON Format)
    try:
        _ensure_log_dir()
        log_file = os.path.join(LOG_DIR, "multi_agent.log")
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG) # Dosyaya daha detaylı yaz
        file_handler.setFormatter(JsonFormatter())
        logger.addHandler(file_handler)
    except Exception as e:
        # Dosya sistemine yazılamazsa sadece konsola yazmaya devam et
        logger.warning(f"Log dosyası oluşturulamadı: {e}")

    return logger


def get_langfuse_handler() -> Optional[object]:
    """
    LangFuse callback handler oluşturur (opsiyonel/bonus).

    LangFuse, LLM uygulamaları için gözlemlenebilirlik (observability) platformudur.
    Proje konfigürasyonunda API anahtarları varsa aktifleşir.

    Returns:
        Optional: LangFuse CallbackHandler veya None.
    """
    try:
        from src.config import LANGFUSE_PUBLIC_KEY, LANGFUSE_SECRET_KEY, LANGFUSE_HOST

        # Anahtarlar eksikse devre dışı bırak
        if not LANGFUSE_PUBLIC_KEY or not LANGFUSE_SECRET_KEY:
            return None

        from langfuse.callback import CallbackHandler

        handler = CallbackHandler(
            public_key=LANGFUSE_PUBLIC_KEY,
            secret_key=LANGFUSE_SECRET_KEY,
            host=LANGFUSE_HOST,
        )

        logger = get_logger(__name__)
        logger.info(
            "LangFuse monitoring aktif",
            extra={"host": LANGFUSE_HOST},
        )
        return handler

    except ImportError:
        # Kütüphane yüklü değilse sessizce geç
        return None
    except Exception:
        return None
