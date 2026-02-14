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

    Tehlikeli modül kullanımını (os, subprocess vb.), dosya işlemlerini ve
    sistem çağrılarını regex analizi ile tespit eder.

    Args:
        code: Kontrol edilecek Python kodu.

    Returns:
        tuple: (güvenli_mi, hata_mesaji)
    """
    # 1. Boş Kod Kontrolü
    if not code or not code.strip():
        return False, "Boş kod gönderildi."

    # 2. Tehlikeli Modül/Fonksiyon Kontrolü
    # Yasaklı listesindeki (BLOCKED_MODULES) her modül için kod taraması yap
    for blocked in BLOCKED_MODULES:
        # Regex desenleri:
        # - import os
        # - from os
        # - os.system(
        patterns = [
            rf'\bimport\s+{re.escape(blocked)}\b',   # import os
            rf'\bfrom\s+{re.escape(blocked)}\b',     # from os import ...
            rf'\b{re.escape(blocked)}\s*\(',         # eval(...)
        ]
        for pattern in patterns:
            if re.search(pattern, code):
                return False, (
                    f"Güvenlik ihlali: '{blocked}' kullanımına izin verilmiyor. "
                    f"Engellenen modüller: {', '.join(BLOCKED_MODULES)}"
                )

    # 3. Built-in Fonksiyon Manipülasyonu Kontrolü
    # __builtins__ erişimi, sandbox kaçışlarına yol açabilir.
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
        str: Kodun çıktısı (stdout) veya hata mesajı.
    """
    logger.info(
        "Kod çalıştırma isteği",
        extra={"code_length": len(code)},
    )

    # 1. Güvenlik Kontrolü
    # Kodu çalıştırmadan ÖNCE analiz et
    is_safe, error_msg = validate_code(code)
    if not is_safe:
        logger.warning(
            "Güvenlik kontrolü başarısız",
            extra={"error": error_msg},
        )
        return f"Güvenlik Hatası: {error_msg}"

    try:
        # 2. Geçici Dosya Oluşturma
        # Kodu çalıştırmak için diskte geçici bir .py dosyası oluşturuyoruz.
        # delete=False çünkü dosyayı kapatıp subprocess ile açacağız.
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".py",
            delete=False,
            encoding="utf-8",
        ) as tmp_file:
            tmp_file.write(code)
            tmp_path = tmp_file.name

        try:
            # 3. Subprocess ile Çalıştırma
            # Yeni bir Python process'i başlatıyoruz. Ana process'ten izole.
            result = subprocess.run(
                ["python", tmp_path],
                capture_output=True,            # Çıktıları yakala
                text=True,                      # String olarak döndür (byte değil)
                timeout=CODE_EXECUTION_TIMEOUT, # Sonsuz döngü koruması
                encoding="utf-8",
            )

            output = result.stdout.strip()
            error = result.stderr.strip()

            # 4. Hata Kontrolü (Return Code)
            if result.returncode != 0:
                logger.warning(
                    "Kod çalıştırma hatası",
                    extra={"returncode": result.returncode, "stderr": error},
                )
                return f"Çalıştırma Hatası:\n{error}"

            # 5. Boş Çıktı Kontrolü
            if not output and not error:
                return "Kod başarıyla çalıştı ancak çıktı üretmedi (print kullandınız mı?)."

            logger.info(
                "Kod başarıyla çalıştırıldı",
                extra={"output_length": len(output)},
            )
            return f"Çıktı:\n{output}"

        finally:
            # 6. Temizlik
            # İşimiz bitince veya hata olsa bile geçici dosyayı sil
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    except subprocess.TimeoutExpired:
        # Zaman aşımı hatasını özel olarak işle
        logger.warning(
            "Kod çalıştırma zaman aşımı",
            extra={"timeout": CODE_EXECUTION_TIMEOUT},
        )
        return (
            f"Zaman Aşımı: Kod {CODE_EXECUTION_TIMEOUT} saniye içinde "
            f"tamamlanamadı. Sonsuz döngü veya ağır işlem olabilir."
        )

    except Exception as e:
        # Diğer tüm hatalar
        error_msg = f"Beklenmeyen hata: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return f"Hata: {error_msg}"
