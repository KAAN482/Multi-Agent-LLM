"""
Multi-Agent LLM Asistanı - Ana Giriş Noktası (CLI)

Kullanıcıdan sorgu alır ve çok ajanlı sistemi çalıştırır.
Komut satırından veya interaktif modda kullanılabilir.

Kullanım:
    python main.py "Sorunuz burada"
    python main.py --mode fast "Sorunuz burada"
    python main.py  # İnteraktif mod
"""

import sys
import argparse
import asyncio
from src.orchestrator.graph import run_multi_agent
from src.utils.logger import get_logger

logger = get_logger(__name__)



def print_banner():
    """Uygulama başlangıç banner'ını yazdırır."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║           Multi-Agent LLM Asistanı v1.0                      ║
║                                                              ║
║  Modeller: Gemini 2.5 Flash (Bulut) + Llama 3.2 3B (Yerel)  ║
║  Ajanlar:  Supervisor | Researcher | Coder | Reviewer | Fmt  ║
║  Araclar:  Web Arama | Kod Calistirma | MCP                 ║
║                                                              ║
║  Cikmak icin 'q' veya 'quit' yazin                          ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_result(result: dict):
    """
    Sonuçları kullanıcı dostu formatlanmış şekilde yazdırır.
    
    Args:
        result: run_multi_agent fonksiyonundan dönen sonuç sözlüğü.
    """
    print("\n" + "=" * 60)
    print("[SONUC]")
    print("=" * 60)
    print(result.get("answer", "Yanıt yok."))
    print("\n" + "-" * 60)
    print(f"[Istatistikler]:")
    print(f"   Iterasyon sayisi: {result.get('iterations', 0)}")
    
    models = result.get("models_used", []) or ["Yok"]
    tools = result.get("tools_called", []) or ["Yok"]
    
    print(f"   Kullanilan modeller: {', '.join(models)}")
    print(f"   Cagrilan tool'lar: {', '.join(tools)}")
    print("=" * 60)


async def interactive_mode(mode: str = "auto"):
    """
    İnteraktif mod: Kullanıcıdan sürekli sorgu alır (Chat döngüsü).

    Args:
        mode: Model seçim modu ("fast", "accurate", "auto").
    """
    print_banner()
    print(f"📌 Aktif mod: {mode}\n")

    while True:
        try:
            # Kullanıcı girdisi al
            try:
                query = input("[?] Sorunuz: ").strip()
            except EOFError:
                break

            if not query:
                print("⚠️  Lütfen bir soru yazın.\n")
                continue

            # Çıkış komutları
            if query.lower() in ("q", "quit", "exit", "çık", "çıkış"):
                print("\n[!] Gule gule! Iyi gunler.")
                break

            # Mod değiştirme komutu (/mode fast, /mode auto vb.)
            if query.startswith("/mode"):
                parts = query.split()
                if len(parts) == 2 and parts[1] in ("fast", "accurate", "auto"):
                    mode = parts[1]
                    print(f"[+] Mod degistirildi: {mode}\n")
                else:
                    print("[!] Kullanım: /mode [fast|accurate|auto]\n")
                continue

            print(f"\n[*] Isleniyor... (mod: {mode})\n")
            
            # Sistemi çalıştır
            result = await run_multi_agent(query, mode=mode)
            
            # Sonuçları göster
            print_result(result)
            print()

        except KeyboardInterrupt:
            # Ctrl+C ile güvenli çıkış
            print("\n\n[!] Gule gule!")
            break
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}", exc_info=True)
            print(f"\n[!] Hata: {str(e)}\n")


def main():
    """Ana fonksiyon: CLI argümanlarını parse eder ve çalıştırır."""
    parser = argparse.ArgumentParser(
        description="Multi-Agent LLM Asistanı - Çok Ajanlı Yapay Zeka Sistemi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Örnekler:
  python main.py "Python'da fibonacci dizisini hesapla"
  python main.py --mode fast "Merhaba, nasılsın?"
  python main.py --mode accurate "Yapay zeka trendlerini araştır"
  python main.py  # İnteraktif mod
        """,
    )
    parser.add_argument(
        "query",
        nargs="?",
        default=None,
        help="Sorgu metni (boş bırakılırsa interaktif mod açılır)",
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["fast", "accurate", "auto"],
        default="auto",
        help="Model seçim modu (varsayılan: auto)",
    )

    args = parser.parse_args()

    if args.query:
        # Tek sorgu modu (Tek sefer çalışır ve çıkar)
        logger.info(
            "Tek sorgu modu başlatılıyor",
            extra={"query": args.query, "mode": args.mode},
        )
        try:
            result = asyncio.run(run_multi_agent(args.query, mode=args.mode))
            print_result(result)
        except Exception as e:
            logger.error(f"Kritik hata: {e}", exc_info=True)
            print(f"[!] Kritik Hata: {e}")
            sys.exit(1)
    else:
        # İnteraktif mod (Sürekli çalışır)
        asyncio.run(interactive_mode(mode=args.mode))


if __name__ == "__main__":
    main()
