# 🤖 Çok Ajanlı LLM Asistanı (Multi-Agent LLM Assistant)

**Gemini 2.5 Flash (Bulut)** ve **Llama 3.2 3B (Yerel/Ollama)** modellerini hibrit olarak kullanan, **LangGraph** tabanlı gelişmiş bir çok ajanlı yapay zeka asistanıdır.

Bu proje, karmaşık görevleri parçalara bölerek uzman ajanlar arasında dağıtır ve en uygun maliyet/performans dengesini sağlamak için görev türüne göre model seçimi yapar.

---

## 🚀 Özellikler

- **Hibrit Model Mimarisi:**
  - **Gemini 2.5 Flash:** Karmaşık analiz, kodlama ve planlama görevleri için (Yüksek zeka, geniş bağlam).
  - **Llama 3.2 3B (Ollama):** Basit konuşma, formatlama ve kontrol görevleri için (Hızlı, ücretsiz, yerel).
  - **Akıllı Router:** Sorguyu analiz edip en uygun modele yönlendirir.

- **Uzman Ajan Kadrosu:**
  - **🤵 Supervisor (Yönetici):** Kullanıcı isteğini analiz eder ve işi doğru ajana atar.
  - **🔎 Researcher (Araştırmacı):** DuckDuckGo kullanarak internetten güncel bilgi toplar.
  - **💻 Coder (Yazılımcı):** Python kodu yazar ve güvenli bir ortamda çalıştırıp sonuç üretir.
  - **👀 Reviewer (Denetçi):** Diğer ajanların çıktılarını doğrular ve hatasız olduğundan emin olur.
  - **📝 Formatter (Düzenleyici):** Sonuçları derleyip kullanıcıya sunulacak profesyonel formata sokar.

- **Güçlü Araçlar (Tools):**
  - **Web Search:** İnternet erişimi (DuckDuckGo).
  - **Code Executor:** Güvenli Python kod çalıştırma ortamı (Sandbox).
  - **MCP (Model Context Protocol):** Standartlaştırılmış tool arayüzü desteği.

- **Gelişmiş Altyapı:**
  - **LangGraph:** Döngüsel ve durum tabanlı (stateful) ajan orkestrasyonu.
  - **Loglama:** JSON formatında detaylı loglama (istekler, hatalar, kullanılan modeller).
  - **Monitoring:** LangFuse entegrasyonu (opsiyonel).

---

## 🛠️ Kurulum

### Gereksinimler
- Python 3.10 veya üzeri
- [Ollama](https://ollama.com/) (Yerel model için)
- Google AI Studio API Anahtarı (Gemini için)

### Adım 1: Projeyi Klonlayın
```bash
git clone https://github.com/KAAN482/Multi-Agent-LLM.git
cd Multi-Agent-LLM
```

### Adım 2: Sanal Ortam Oluşturun
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Adım 3: Bağımlılıkları Yükleyin
```bash
pip install -r requirements.txt
```

### Adım 4: Yerel Modeli İndirin (Ollama)
Ollama'nın kurulu ve çalışıyor olduğundan emin olun, ardından terminalde:
```bash
ollama pull llama3.2:3b
```

### Adım 5: Konfigürasyon (.env)
`.env.example` dosyasının adını `.env` olarak değiştirin ve API anahtarınızı ekleyin:
```ini
# .env dosyası
GEMINI_API_KEY=AIzaSy... (Google AI Studio'dan aldığınız anahtar)

# Opsiyonel: LangFuse kullanacaksanız
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
```

---

## 💻 Kullanım

Projeyi komut satırından (CLI) interaktif olarak veya tek seferlik komutlarla kullanabilirsiniz.

### İnteraktif Mod (Chat)
Sürekli soru-cevap döngüsü için:
```bash
python main.py
```
Çıkmak için `q` veya `quit` yazabilirsiniz.

### Tek Seferlik Sorgu
```bash
python main.py "Python ile fibonacci dizisini hesaplayan bir fonksiyon yaz ve çalıştır"
```

### Mod Seçimi
Farklı çalışma modlarını `--mode` parametresi ile seçebilirsiniz:

- **auto (Varsayılan):** Göreve göre otomatik model seçer.
- **fast:** Mümkünse yerel modeli (Ollama) kullanır. Hız önceliklidir.
- **accurate:** Her zaman güçlü modeli (Gemini) kullanır. Doğruluk önceliklidir.

Örnek:
```bash
python main.py --mode fast "Merhaba, nasılsın?"
python main.py --mode accurate "Kuantum bilgisayarların geleceğini araştır"
```

---

## 📂 Proje Yapısı

```
Multi-Agent-LLM/
├── src/
│   ├── agents/          # Ajan tanımları (Supervisor, Coder, vb.)
│   ├── models/          # LLM wrapper'ları (Gemini, Ollama)
│   ├── tools/           # Araçlar (Web Search, Code Executor)
│   ├── orchestrator/    # LangGraph ve State yönetimi
│   ├── monitoring/      # Logger ve LangFuse entegrasyonu
│   └── config.py        # Ayarlar ve sabitler
├── tests/               # Birim ve entegrasyon testleri
├── logs/                # Çalışma logları (JSON formatında)
├── main.py              # Giriş noktası (CLI)
├── requirements.txt     # Python kütüphaneleri
└── .env                 # API anahtarları (Git'e atılmaz!)
```

---

## 🛡️ Güvenlik Notları
- **Kod Çalıştırma:** `code_executor` modülü, tehlikeli işlemleri (dosya silme, sisteme erişme vb.) engellemek için güvenlik filtrelerine sahiptir, ancak yine de dikkatli olunmalıdır.
- **API Anahtarları:** `.env` dosyanızı asla GitHub'a yüklemeyin (zaten `.gitignore` içinde engellenmiştir).

---

## 🤝 Katkıda Bulunma
1. Bu projeyi forklayın.
2. Yeni bir feature branch açın (`git checkout -b feature/yeni-ozellik`).
3. Değişikliklerinizi yapın ve commit'leyin.
4. Branch'inizi pushlayın (`git push origin feature/yeni-ozellik`).
5. Bir Pull Request oluşturun.

---

## 📜 Lisans
Bu proje MIT lisansı ile lisanslanmıştır.
