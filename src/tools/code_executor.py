"""
Güvenli kod çalıştırma tool modülü.

Python kod parçalarını güvenli bir ortamda çalıştırır.
Tehlikeli modülleri engeller ve timeout ile çalışır.
Hesaplama, veri işleme ve doğrulama görevlerinde kullanılır.
"""

import re
import subprocess
import tempfile
import os
from langchain_core.tools import tool
from src.config import CODE_EXECUTION_TIMEOUT, BLOCKED_MODULES
from src.monitoring.logger import get_logger

logger = get_logger(__name__)


def validate_code(code: str) -> tuple[bool, str]:
    """
    Kod güvenliğini kontrol eder.

    Tehlikeli modül kullanımını, dosya işlemlerini ve
    sistem çağrılarını tespit eder.

    Args:
        code: Kontrol edilecek Python kodu.

    Returns:
        tuple: (güvenli_mi, hata_mesaji)
    """
    # Boş kod kontrolü
    if not code or not code.strip():
        return False, "Boş kod gönderildi."

    # Tehlikeli modül/fonksiyon kontrolü
    for blocked in BLOCKED_MODULES:
        # import blocked, from blocked, blocked( gibi kalıpları ara
        patterns = [
            rf'\bimport\s+{re.escape(blocked)}\b',
            rf'\bfrom\s+{re.escape(blocked)}\b',
            rf'\b{re.escape(blocked)}\s*\(',
        ]
        for pattern in patterns:
            if re.search(pattern, code):
                return False, (
                    f"Güvenlik ihlali: '{blocked}' kullanımına izin verilmiyor. "
                    f"Engellenen modüller: {', '.join(BLOCKED_MODULES)}"
                )

    # __builtins__ manipülasyonu kontrolü
    if "__builtins__" in code:
        return False, "Güvenlik ihlali: __builtins__ erişimine izin verilmiyor."

    return True, ""


@tool
def code_executor_tool(code: str) -> str:
    """
    Python kodunu güvenli bir ortamda çalıştırır ve sonucunu döndürür.

    Hesaplama, veri işleme ve doğrulama görevleri için kullanılır.
    Güvenlik kontrolleri uygulanır: tehlikeli modüller engellenir,
    zaman aşımı sınırı vardır.

    Args:
        code: Çalıştırılacak Python kodu.

    Returns:
        str: Kodun çıktısı veya hata mesajı.
    """
    logger.info(
        "Kod çalıştırma isteği",
        extra={"code_length": len(code)},
    )

    # Güvenlik kontrolü
    is_safe, error_msg = validate_code(code)
    if not is_safe:
        logger.warning(
            "Güvenlik kontrolü başarısız",
            extra={"error": error_msg},
        )
        return f"Güvenlik Hatası: {error_msg}"

    try:
        # Geçici dosyaya yaz ve subprocess ile çalıştır
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as tmp_file:
            tmp_file.write(code)
            tmp_path = tmp_file.name

        try:
            result = subprocess.run(
                ["python", tmp_path],
                capture_output=True,
                text=True,
                timeout=CODE_EXECUTION_TIMEOUT,
                encoding="utf-8",
            )

            output = result.stdout.strip()
            error = result.stderr.strip()

            if result.returncode != 0:
                logger.warning(
                    "Kod çalıştırma hatası",
                    extra={"returncode": result.returncode, "stderr": error},
                )
                return f"Çalıştırma Hatası:\n{error}"

            if not output and not error:
                return "Kod başarıyla çalıştı ancak çıktı üretmedi."

            logger.info(
                "Kod başarıyla çalıştırıldı",
                extra={"output_length": len(output)},
            )
            return f"Çıktı:\n{output}"

        finally:
            # Geçici dosyayı temizle
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    except subprocess.TimeoutExpired:
        logger.warning(
            "Kod çalıştırma zaman aşımı",
            extra={"timeout": CODE_EXECUTION_TIMEOUT},
        )
        return (
            f"Zaman Aşımı: Kod {CODE_EXECUTION_TIMEOUT} saniye içinde "
            f"tamamlanamadı. Sonsuz döngü veya ağır işlem olabilir."
        )

    except Exception as e:
        error_msg = f"Beklenmeyen hata: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return f"Hata: {error_msg}"
