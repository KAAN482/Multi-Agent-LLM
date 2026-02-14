# 🧠 Multi-Agent LLM Asistanı

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![LangChain](https://img.shields.io/badge/LangChain-0.3-green)
![FastAPI](https://img.shields.io/badge/FastAPI-Modern-teal)

Bu proje, yerel (**Llama 3.2 via Ollama**) ve bulut (**Gemini 2.5 Flash**) modellerini hibrit olarak kullanan, **LangGraph** tabanlı gelişmiş bir çoklu ajan (multi-agent) yapay zeka sistemidir. Hem komut satırı (CLI) hem de modern bir Web Arayüzü ile gelir.

---

## 🌟 Özellikler

### 🤖 1. Çok Ajanlı Mimari (Multi-Agent)
Sistem, tek bir LLM yerine uzmanlaşmış ajanlardan oluşan bir ekip gibi çalışır:
- **🤵 Supervisor (Analist):** Kullanıcı isteğini analiz eder, RAG ile bilgi toplar ve görevi yönlendirir.
- **🔎 Master Agent (Yönetici):** Tüm bilgileri sentezler, eksik varsa internet araması yapar ve nihai yanıtı üretir.
- **💻 Logic Expert (Mantık/Kod):** Karmaşık hesaplamalar ve kod yazma görevlerini üstlenir.

### 🧠 2. Hibrit Model Yapısı
Maliyet ve performansı optimize etmek için görev karmaşıklığına göre model seçimi yapılır:
- **Llama 3.2 3B (Yerel):** Hızlı analiz, yönlendirme ve özetleme.
- **Gemini 2.5 Flash (Bulut):** Derin mantık, kod yazma ve son kullanıcı yanıtı.

### 🛠️ 3. Gelişmiş Araçlar (Tools)
- **🌍 Web Search:** DuckDuckGo ile güncel internet bilgisi (Rate limit korumalı).
- **📚 RAG (Doküman Analizi):** PDF/DOCX/TXT dosyalarından vektör tabanlı bilgi çekme.
- **🐍 Code Executor:** Python kodlarını güvenli bir ortamda çalıştırıp sonuç üretme.

### 💻 4. Modern Web Arayüzü
- **FastAPI** tabanlı güçlü backend.
- **Glassmorphism** tasarımlı, karanlık mod destekli şık frontend.
- Markdown destekli sohbet ekranı.
- Sürükle-bırak dosya yükleme.

---

## 🏗️ Mimari

```mermaid
graph TD
    User[Kullanıcı] -->|Sorgu| API[FastAPI / CLI]
    API --> Analyst[Analist (Llama 3.1)]
    
    Analyst -->|RAG ile Bilgi Topla| RAG[(Vektör DB)]
    Analyst -->|Yönlendirme| Router{Karar Mekanizması}
    
    Router -->|Hesaplama Gerekli| Logic[Mantık Uzmanı (DeepSeek)]
    Router -->|Genel Bilgi| Master[Master Agent (Gemini 2.5)]
    
    Logic -->|Sonuç| Master
    
    Master -->|İnternet Araması| Web[DuckDuckGo]
    Master -->|Nihai Yanıt| API
```

---

## 🚀 Kurulum

### Gereksinimler
- Python 3.10+
- [Ollama](https://ollama.com/) uygulaması
- Google AI Studio API Anahtarı

### Adım 1: Depoyu Klonlayın
```bash
git clone https://github.com/KAAN482/Multi-Agent-LLM.git
cd Multi-Agent-LLM
```

### Adım 2: Sanal Ortam Oluşturun
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### Adım 3: Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### Adım 4: Yerel Modeli İndirin
```bash
ollama pull llama3.2:3b
```

### Adım 5: Çevresel Değişkenler (.env)
Proje ana dizininde `.env` dosyası oluşturun ve anahtarınızı ekleyin:
```ini
GEMINI_API_KEY=AIzzaSy...
OLLAMA_BASE_URL=http://localhost:11434
```

---

## 💻 Kullanım

### Seçenek 1: Web Arayüzü (Önerilen)
Web sunucusunu başlatın:
```bash
python -m uvicorn rag_app.main:app --reload
```
Ardından tarayıcınızda **http://localhost:8000** adresine gidin.

### Seçenek 2: CLI (Komut Satırı)
Doğrudan terminal üzerinden sohbet edin:
```bash
python main.py
```
Veya tek seferlik sorgu gönderin:
```bash
python main.py "Fenerbahçe başkanı kim?"
```

---

## 📂 Proje Yapısı

```
Multi-Agent-LLM/
├── src/                 # Çekirdek Ajan Mantığı
│   ├── agents/          # Ajan tanımları (Analyst, Master, Logic)
│   ├── orchestrator/    # LangGraph iş akışı
│   ├── tools/           # Araçlar (Web, RAG, Code)
│   └── models/          # Model istemcileri
├── rag_app/             # Web Uygulaması (FastAPI)
│   ├── startic/         # Frontend (HTML/CSS/JS)
│   ├── services/        # RAG ve Embedding servisleri
│   └── main.py          # API Endpoint'leri
├── main.py              # CLI Giriş Noktası
├── requirements.txt     # Bağımlılıklar
└── README.md            # Dokümantasyon
```

## 🤝 Katkıda Bulunma
Bu proje açık kaynaklıdır. Katkılarınızı bekleriz! Lütfen Pull Request göndermeden önce testleri çalıştırın.

---
**Lisans:** MIT
