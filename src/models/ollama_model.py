"""
Ollama model wrapper modülü.

Yerel Llama 3.2 3B modelini Ollama üzerinden LangChain'e bağlar.
Basit görevler için düşük gecikme süresiyle yanıt verir.
"""

import requests
from langchain_community.chat_models import ChatOllama
from src.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL_NAME,
    OLLAMA_TEMPERATURE,
    OLLAMA_MAX_TOKENS,
)
from src.monitoring.logger import get_logger

logger = get_logger(__name__)


def check_ollama_connection() -> bool:
    """
    Ollama sunucusunun çalışıp çalışmadığını kontrol eder.

    Returns:
        bool: Bağlantı başarılıysa True, değilse False.
    """
    try:
        response = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        return response.status_code == 200
    except requests.ConnectionError:
        logger.warning(
            "Ollama sunucusuna bağlanılamadı",
            extra={"url": OLLAMA_BASE_URL},
        )
        return False
    except Exception as e:
        logger.error(
            "Ollama bağlantı kontrolünde beklenmeyen hata",
            extra={"error": str(e)},
        )
        return False


def get_ollama_model(
    temperature: float = None,
    max_tokens: int = None,
) -> ChatOllama:
    """
    Ollama üzerinden Llama 3.2 3B modelini başlatır ve döndürür.

    Args:
        temperature: Yaratıcılık seviyesi (0.0-1.0). None ise config değeri kullanılır.
        max_tokens: Maksimum üretilecek token sayısı. None ise config değeri kullanılır.

    Returns:
        ChatOllama: LangChain uyumlu Ollama model nesnesi.

    Raises:
        ConnectionError: Ollama sunucusu çalışmıyorsa.
    """
    if not check_ollama_connection():
        raise ConnectionError(
            f"Ollama sunucusu ({OLLAMA_BASE_URL}) çalışmıyor. "
            "Lütfen Ollama'yı başlatın: https://ollama.com\n"
            f"Model indirme: ollama pull {OLLAMA_MODEL_NAME}"
        )

    temp = temperature if temperature is not None else OLLAMA_TEMPERATURE
    tokens = max_tokens if max_tokens is not None else OLLAMA_MAX_TOKENS

    logger.info(
        "Ollama modeli başlatılıyor",
        extra={
            "model": OLLAMA_MODEL_NAME,
            "base_url": OLLAMA_BASE_URL,
            "temperature": temp,
            "max_tokens": tokens,
        },
    )

    model = ChatOllama(
        model=OLLAMA_MODEL_NAME,
        base_url=OLLAMA_BASE_URL,
        temperature=temp,
        num_predict=tokens,
    )

    logger.info("Ollama modeli başarıyla başlatıldı")
    return model
