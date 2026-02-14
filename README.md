# 🤖 Multi-Agent LLM Asistanı (Hafta 2)

Bu proje, yerel (Llama 3.2 via Ollama) ve bulut (Gemini 2.5 Flash) modellerini hibrit olarak kullanan, **LangGraph** tabanlı gelişmiş bir çok ajanlı yapay zeka sistemidir.

## 🎯 Hafta 2 Hedefleri ve Özellikleri

### 1. Çok Ajanlı Mimari (Multi-Agent)
Sistem, tek bir LLM yerine özelleşmiş ajanlardan oluşan bir ekip gibi çalışır:
- **🤵 Supervisor (Yönetici):** Kullanıcı isteğini analiz eder ve işi doğru ajana (Researcher, Coder veya RAGSpecialist) atar.
- **🔎 Researcher (Araştırmacı):** DuckDuckGo kullanarak internetten güncel bilgi toplar.
- **💻 Coder (Yazılımcı):** Python kodu yazar ve güvenli bir ortamda çalıştırıp sonuç üretir.
- **📚 RAG Specialist (Doküman Uzmanı):** PDF/DOCX dokümanlarından bilgi çeker.

### 2. Akıllı Model Yönlendirme (Routing)
Maliyet ve performansı optimize etmek için görev karmaşıklığına göre model seçimi yapılır:
- **Llama 3.2 3B (Ollama):** Basit konuşmalar, yönlendirme kararları ve özetleme için (Hızlı, Yerel).
- **Gemini 2.5 Flash:** Karmaşık mantık yürütme, kod yazma ve derin analiz için (Akıllı, Bulut).

### 3. Araçlar (Tools)
- **Web Search:** İnternet erişimi (DuckDuckGo).
- **Code Executor:** Güvenli Python kod çalıştırma ortamı (Sandbox).
- **RAG Tool:** Yerel dokümanlarda semantik arama.

---

## 🛠️ Kurulum

### Gereksinimler
- Python 3.10+
- [Ollama](https://ollama.com/) (ve `llama3.2:3b` modeli)
- Google AI Studio API Anahtarı

### Adım 1: Kurulum ve Bağımlılıklar
```bash
git clone <repo-url>
cd Multi-Agent-LLM
python -m venv venv
# Windows: venv\Scripts\activate
# Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

### Adım 2: Çevresel Değişkenler (.env)
```ini
GEMINI_API_KEY=AIzzaSy...
OLLAMA_BASE_URL=http://localhost:11434
```

### Adım 3: Yerel Modeli Hazırla
```bash
ollama pull llama3.2:3b
```

---

## 💻 Kullanım

### CLI Modu (Önerilen)
Sistemi komut satırından yönetebilirsiniz:

**1. İnteraktif Sohbet:**
```bash
python main.py
```

**2. Tek Seferlik Sorgular:**
```bash
python main.py "Python ile fibonacci dizisini hesapla"
python main.py "Fransa'nın başkenti neresidir?"
```

---

## 📂 Proje Yapısı

```
Multi-Agent-LLM/
├── src/
│   ├── agents/          # Ajan tanımları (Supervisor, Researcher, Coder...)
│   ├── models/          # LLM wrapper'ları (Gemini, Ollama) ve Router
│   ├── tools/           # Araçlar (Web, Kod, RAG)
│   ├── orchestrator/    # LangGraph akış yönetimi
│   ├── utils/           # Yardımcı fonksiyonlar (Logger vb.)
│   └── config.py        # Ayarlar
├── main.py              # CLI Giriş Noktası
├── rag_app/             # (Hafta 1) RAG Backend Modülü
├── legacy_agents/       # (Eski) Arşiv
└── requirements.txt     # Bağımlılıklar
```

## 🤝 Katkıda Bulunma
- Feature branch (`feature/agents`, `feature/tools`) mantığı ile geliştirilmiştir.
- PEP8 standartlarına uyulmuştur.
