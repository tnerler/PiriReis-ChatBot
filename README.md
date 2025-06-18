# PIRIX – Üniversite Chatbotu (RAG Tabanlı)
PIRIX, üniversite web sitesindeki içerikleri anlamlandırarak kullanıcı sorularına anlamlı cevaplar üreten bir Retrieval-Augmented Generation (RAG) tabanlı chatbot sistemidir.
Amaç, üniversiteye dair bilgi akışını otomatikleştirmek ve öğrencilere yapay zeka destekli bir asistan sunmaktır.

## Proje Yapısı
```
PIRIX/
├── get_data/              # Ham veri çekme işlemleri (API, scraping vs.)
├── tag_embeddings/        # Tag'lerin embedding'lerinin tutulduğu yer
├── vector_db/             # FAISS vektör veritabanı dosyaları
├── _faiss.py              # FAISS'e embedding ekleme & sorgulama modülü
├── config.py              # Ortam ayarları (API key, model vs.)
├── load_docs.py           # Dosyaları LangChain Document listesine çevirme
├── main.py                # Ana uygulama (pipeline başlatıcı)
├── openai_clients.py      # OpenAI embedding & completion client
├── retrieve_and_generate.py # RAG sürecinin yürütüldüğü ana modül
├── tag_embeddings.py      # Tag embedding hesaplama ve saklama
├── .env                   # Ortam değişkenleri
├── .gitignore             # Versiyon kontrolü dışında bırakılan dosyalar
└── requirements.txt       # Gerekli Python paketleri
```
## ⚙️ Ortam Değişkenleri (.env)

```env
OPENAI_API_KEY=your_openai_api_key
LANGSMITH_TRACING=true # Opsiyonel
LANGSMITH_API_KEY=your_langsmith_api_key # Opsiyonel
```
**Langsmith ile model çıktılarınızı takip etmek için LANGSMITH_TRACING=true ve API anahtarınızı eklemeyi unutmayın.**
## Kullanım
```
python main.py
```
**Bu komut, dökümanları yükler, vektör veritabanını hazırlar, OpenAI ile soruları cevaplayan sistemi başlatır.**

## Teknolojiler
* LangChain – Döküman işleme ve RAG pipeline yönetimi

* FAISS – Vektör arama veritabanı

* OpenAI API – Embedding ve metin üretimi

* Python – Tüm backend

* dotenv – Ortam değişkenleri yönetimi
## Notlar
* Web scraping işlemleri **get_data/** klasöründe yönetilir.

* Tag Embedding'ler **tag_embeddings/** altında güncellenir. Versiyon kontrolü dışındadır.

* FAISS veritabanı **vector_db/** içinde saklanır. Versiyon kontrolü dışındadır.
## 🤝 Katkı Sağla

Bu projeye katkıda bulunmak isterseniz:

- Projeyi forkladıktan sonra geliştirmeler yapabilir ve pull request açabilirsiniz.  
- Projede gördüğünüz hatalar veya öneriler için issue açabilirsiniz.  
- Dokümantasyon, test veya yeni özellik ekleyerek katkı sağlayabilirsiniz.

Her türlü katkı değerlidir, teşekkürler! 💙
