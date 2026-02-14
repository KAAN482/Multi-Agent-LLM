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
from src.orchestrator.graph import run_multi_agent
from src.monitoring.logger import get_logger

logger = get_logger(__name__)


def print_banner():
    """Uygulama başlangıç banner'ını yazdırır."""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║           🤖 Multi-Agent LLM Asistanı v1.0 🤖              ║
║                                                              ║
║  Modeller: Gemini 2.5 Flash (Bulut) + Llama 3.2 3B (Yerel)  ║
║  Ajanlar:  Supervisor | Researcher | Coder | Reviewer | Fmt  ║
║  Araçlar:  Web Arama | Kod Çalıştırma | MCP                 ║
║                                                              ║
║  Çıkmak için 'q' veya 'quit' yazın                          ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(banner)


def print_result(result: dict):
    """Sonuçları formatlanmış şekilde yazdırır."""
    print("\n" + "=" * 60)
    print("📋 SONUÇ")
    print("=" * 60)
    print(result["answer"])
    print("\n" + "-" * 60)
    print(f"📊 İstatistikler:")
    print(f"   İterasyon sayısı: {result['iterations']}")
    print(f"   Kullanılan modeller: {', '.join(result['models_used']) or 'Yok'}")
    print(f"   Çağrılan tool'lar: {', '.join(result['tools_called']) or 'Yok'}")
    print("=" * 60)


def interactive_mode(mode: str = "auto"):
    """
    İnteraktif mod: Kullanıcıdan sürekli sorgu alır.

    Args:
        mode: Model seçim modu ("fast", "accurate", "auto").
    """
    print_banner()
    print(f"📌 Aktif mod: {mode}\n")

    while True:
        try:
            query = input("❓ Sorunuz: ").strip()

            if not query:
                print("⚠️  Lütfen bir soru yazın.\n")
                continue

            if query.lower() in ("q", "quit", "exit", "çık", "çıkış"):
                print("\n👋 Güle güle! İyi günler.")
                break

            # Mod değiştirme komutu
            if query.startswith("/mode"):
                parts = query.split()
                if len(parts) == 2 and parts[1] in ("fast", "accurate", "auto"):
                    mode = parts[1]
                    print(f"✅ Mod değiştirildi: {mode}\n")
                else:
                    print("⚠️  Kullanım: /mode [fast|accurate|auto]\n")
                continue

            print(f"\n🔄 İşleniyor... (mod: {mode})\n")
            result = run_multi_agent(query, mode=mode)
            print_result(result)
            print()

        except KeyboardInterrupt:
            print("\n\n👋 Güle güle!")
            break
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}", exc_info=True)
            print(f"\n❌ Hata: {e}\n")


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
        # Tek sorgu modu
        logger.info(
            "Tek sorgu modu",
            extra={"query": args.query, "mode": args.mode},
        )
        result = run_multi_agent(args.query, mode=args.mode)
        print_result(result)
    else:
        # İnteraktif mod
        interactive_mode(mode=args.mode)


if __name__ == "__main__":
    main()
