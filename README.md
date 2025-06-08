PIRIX/
│
├── get_data/               # 📥 Ham veri çekme işlemleri (API, scraping vs.) - Projeye veri sağlamak için kullanılan ham veri kaynakları burada toplanır.
├── tag_embeddings/         # 🏷️ Tag'lerin embedding’lerinin tutulduğu yer - Tag'lerin vektör temsilleri burada saklanır.
├── vector_db/              # 📦 FAISS vektör veritabanının kaydedildiği klasör - FAISS indeks dosyaları bu klasörde yer alır.
│
├── _faiss.py               # ⚙️ FAISS ile embedding'leri vektör veritabanına ekleme & sorgulama - Vektör veritabanı oluşturma ve sorgulama fonksiyonları, dokümanları chunk'lara ayırma + yükleme işlemleri - Metinlerin parçalara bölünüp işlenmesi burada gerçekleşir.
├── config.py               # ⚙️ API key'ler, path'ler, model ayarları (konfigürasyon dosyası) - Projenin tüm konfigürasyon parametreleri burada.
├── load_docs.py            # 📚 Dosylari LangChaing Document listesi haline getirip yükleme işlemleri burada gerceklesir.
├── main.py                 # 🚀 Ana uygulama dosyası (pipeline başlatıcısı) - Projenin giriş noktası, tüm işlemleri başlatır.
├── openai_clients.py       # 🤖 OpenAI model client (embedding & completion interface’i) - OpenAI API’sine bağlanma, embedding ve completion işlemleri.
├── retrieve_and_generate.py# 🔍 RAG: en iyi dokümanı bul ve cevap oluştur - Retrieval-augmented generation işlemlerinin yürütüldüğü modül.
├── tag_embeddings.py       # 🧠 Tag'leri embedle ve `.pkl` dosyasına kaydet - Tag embedding hesaplama ve kaydetme işlemi burada.
│
├── .env                    # 🔐 Ortam değişkenleri (API key vs.) - Gizli anahtarlar ve ortam değişkenleri.
├── .gitignore              # 🧹 Versiyon kontrolüne dahil edilmeyecek dosyalar - Git tarafından yok sayılacak dosya ve klasörler.
├── requirements.txt        # 📦 Gerekli Python paketleri listesi - Projede kullanılan Python kütüphanelerinin listesi.
