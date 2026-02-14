# Çok Ajanlı LLM Sistemi Sunumu

## 1. Proje Amacı ve Kapsamı
Bu proje, modern yapay zeka mimarilerini kullanarak maliyet etkin, hızlı ve yüksek doğruluklu bir asistan sistemi oluşturmayı hedefler. Hibrit bir yaklaşım benimseyerek bulut tabanlı güçlü modeller ile yerel çalışan hafif modelleri aynı iş akışında birleştirir.

## 2. Ajan Rolleri ve Sorumluluklar
*   **Supervisor (Yönetici)**: İş akışının orkestrasyonunu sağlar. Gelen talebi analiz eder ve ilgili alt ajanlara yönlendirir.
*   **Researcher (Araştırmacı)**: DuckDuckGo arama motoru üzerinden internette güncel bilgi taraması yapar ve kaynakları derler.
*   **Coder (Kodlayıcı)**: Karmaşık matematiksel hesaplamalar ve veri işleme görevleri için Python kodu üretir ve güvenli bir alanda (sandbox) çalıştırır.
*   **Reviewer (Denetleyici)**: Ajanlardan gelen çıktıları doğruluk, tutarlılık ve kalite açısından kontrol eder. (Yerel Llama 3.2 üzerinde çalışır).
*   **Formatter (Düzenleyici)**: Toplanan tüm bilgileri kullanıcı dostu Markdown formatına çevirir ve Türkçe dil desteğini garanti eder.

## 3. Hibrit Model Stratejisi
*   **Gemini 2.5 Flash**: Yüksek muhakeme gerektiren "Supervisor", "Researcher" ve "Coder" görevleri için seçilmiştir. Büyük bağlam penceresi (context window) ve ücretsiz API desteği avantajdır.
*   **Llama 3.2 3B**: Basit kontrol ve formatlama görevleri için "Reviewer" ve "Formatter" rollerinde kullanılır. Ollama ile yerel çalışması sayesinde gecikme süresini azaltır ve API kotalarını korur.

## 4. Kullanılan Teknolojiler
*   **Framework**: LangGraph (Durum tabanlı orkestrasyon)
*   **Kütüphaneler**: LangChain, Google Generative AI, Ollama, DuckDuckGo-Search, Pytest.
*   **İzleme**: JSON tabanlı yapılandırılmış loglama ve LangFuse desteği.
*   **Protokol**: MCP (Model Context Protocol) entegrasyonu.

## 5. Sonuç ve Gelecek Çalışmalar
Proje, karmaşık görevlerin ajanlar arası işbölümü ile nasıl daha verimli çözülebileceğini kanıtlamıştır. Gelecekte sisteme özel veritabanı (RAG) entegrasyonu ve daha gelişmiş MCP sunucuları eklenerek yetenekleri genişletilebilir.
