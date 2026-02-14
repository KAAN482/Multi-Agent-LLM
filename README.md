# Multi-Agent LLM Asistanı

Bu proje, **Gemini 2.5 Flash** (Bulut) ve **Llama 3.2 3B** (Yerel) modellerini hibrit olarak kullanan, **LangGraph** ile optimize edilmiş 5 ajanlı bir asistan sistemidir.

## 🚀 Öne Çıkan Özellikler

*   **Hibrit Model Mimarisi**: Karmaşık akıl yürütme için Gemini, hızlı ve ücretsiz yerel işlemler için Llama 3.2.
*   **Akıllı Model Seçici**: Görev türüne ve metin uzunluğuna göre modeli otomatik belirleyerek API maliyetini ve gecikmeyi optimize eder.
*   **5 Uzman Ajan**: Supervisor, Researcher, Coder, Reviewer ve Formatter ajanları LangGraph üzerinde işbirliği yapar.
*   **Entegre Araçlar**: DuckDuckGo Web Arama, Güvenli Python Kod Executor ve MCP (Model Context Protocol).
*   **Gelişmiş İzleme**: JSON formatlı loglama ve LangFuse entegrasyonu.
*   **%100 Ücretsiz**: Kullanılan tüm modeller ve araçlar ücretsiz katmanları veya yerel kaynakları kullanır.

## 🛠️ Kurulum

1.  **Depoyu Klonlayın**:
    ```bash
    git clone https://github.com/KAAN482/Multi-Agent-LLM.git
    cd Multi-Agent-LLM
    ```

2.  **Sanal Ortam Oluşturun**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    # source venv/bin/activate # Linux/Mac
    ```

3.  **Bağımlılıkları Yükleyin**:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Ollama ve Llama 3.2**:
    *   [ollama.com](https://ollama.com) adresinden Ollama'yı indirin ve kurun.
    *   `ollama pull llama3.2:3b` komutuyla modeli indirin.

5.  **Ortam Değişkenleri**:
    *   `.env.example` dosyasını `.env` olarak kopyalayın.
    *   `GEMINI_API_KEY` değerini [Google AI Studio](https://aistudio.google.com/app/apikey) üzerinden alarak ekleyin.
    *   (Opsiyonel) LangFuse anahtarlarını ekleyin.

## 💻 Kullanım

Sistemi iki modda çalıştırabilirsiniz:

**1. Etkileşimli Mod (Sohbet):**
```bash
python main.py
```

**2. Tek Sorgu Modu:**
```bash
python main.py "Python'da fibonacci dizisinin ilk 10 elemanını hesapla" --mode auto
```

### Mod Seçenekleri:
*   `auto`: Göreve göre otomatik seçim (Varsayılan).
*   `fast`: Yerel Llama modeline öncelik verir.
*   `accurate`: Karmaşık görevler için Gemini 2.5 Flash'a öncelik verir.

## 🧪 Testler

Tüm birim testlerini çalıştırmak için:
```bash
python -m pytest tests/ -v
```

## 🏗️ Mimari

Proje, LangGraph üzerinde tanımlanmış bir durum grafiği kullanır. **Supervisor** ajanı, kullanıcı query'sini analiz ederek Researcher (Araştırma) veya Coder (Hesaplama/Kodlama) ajanlarına iş dağıtır. Sonuçlar **Reviewer** tarafından denetlenir ve **Formatter** tarafından son kullanıcı formatına (Markdown) dönüştürülür.

---
**Geliştirici**: [KAAN482](https://github.com/KAAN482)
