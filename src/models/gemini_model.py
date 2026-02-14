"""
Gemini model wrapper modülü.

Google Gemini 2.5 Flash modelini LangChain üzerinden kullanmak için
wrapper fonksiyon sağlar. Bulut tabanlı, karmaşık görevler için kullanılır.
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from src.config import (
    GEMINI_API_KEY,
    GEMINI_MODEL_NAME,
    GEMINI_TEMPERATURE,
    GEMINI_MAX_TOKENS,
)
from src.monitoring.logger import get_logger

logger = get_logger(__name__)


def get_gemini_model(
    temperature: float = None,
    max_tokens: int = None,
) -> ChatGoogleGenerativeAI:
    """
    Gemini 2.5 Flash modelini başlatır ve döndürür.

    Args:
        temperature: Yaratıcılık seviyesi (0.0-1.0). None ise config değeri kullanılır.
        max_tokens: Maksimum üretilecek token sayısı. None ise config değeri kullanılır.

    Returns:
        ChatGoogleGenerativeAI: LangChain uyumlu Gemini model nesnesi.

    Raises:
        ValueError: API anahtarı tanımlı değilse.
    """
    if not GEMINI_API_KEY:
        raise ValueError(
            "GEMINI_API_KEY tanımlı değil. "
            ".env dosyasında veya ortam değişkenlerinde ayarlayın. "
            "Ücretsiz API key: https://aistudio.google.com/app/apikey"
        )

    temp = temperature if temperature is not None else GEMINI_TEMPERATURE
    tokens = max_tokens if max_tokens is not None else GEMINI_MAX_TOKENS

    logger.info(
        "Gemini modeli başlatılıyor",
        extra={
            "model": GEMINI_MODEL_NAME,
            "temperature": temp,
            "max_tokens": tokens,
        },
    )

    model = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL_NAME,
        google_api_key=GEMINI_API_KEY,
        temperature=temp,
        max_output_tokens=tokens,
    )

    logger.info("Gemini modeli başarıyla başlatıldı")
    return model
