# Proje Klasör Yapısı
```
PIRIX/
├── get_data/ # Ham veri çekme işlemleri (API, scraping vs.)
├── tag_embeddings/ # Tag'lerin embedding’lerinin tutulduğu yer
├── vector_db/ # FAISS vektör veritabanının kaydedildiği klasör
├── _faiss.py # FAISS ile embedding'leri veritabanına ekleme & sorgulama
├── config.py # API key'ler, path'ler, model ayarları
├── load_docs.py # Dosyaları LangChain Document listesine çevirme
├── main.py # Ana uygulama dosyası (pipeline başlatıcısı)
├── openai_clients.py # OpenAI API client (embedding ve completion interface)
├── retrieve_and_generate.py# RAG işlemlerinin yürütüldüğü modül
├── tag_embeddings.py # Tag embedding hesaplama ve kaydetme işlemleri
├── .env # Ortam değişkenleri (API key vs.)
├── .gitignore # Versiyon kontrolüne dahil edilmeyecek dosyalar
└── requirements.txt # Projede kullanılan Python paketlerinin listesi

