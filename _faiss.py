import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from openai_clients import embedding_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os 
from load_docs import compute_hash


def get_existing_hashes(vector_store) -> set:

    """
    Var olan FAISS veritabanındaki tüm belgelerin hash değerlerini toplar.
    Böylece yeni belge eklerken aynı olanları eklemekten kaçınabiliriz.
    """

    hashes = set() # Boş bir küme oluşturduk, buraya bulduğumuz hash'leri ekleyeceğiz.

    # vector_store içindeki tüm belgeleri tek tek dolaşacağız.
    # vector_store.docstore._dict.values() bize depolanan tüm belgelerin listesini verir.
    for doc in vector_store.docstore._dict.values():
        # Her bir belgenin metadata'sından "hash" bilgisini almaya çalışıyoruz.:
        doc_hash = doc.metadata.get("hash")
        if doc_hash:
            hashes.add(doc_hash)
    return hashes



def build_store(docs, persist_path='vector_db') : 

    """
    FAISS vektör veritabanını oluşturur veya var olanı yükler.
    Yeni belgeleri önceki veritabanına ekler, aynı belgeleri hash ile kontrol eder.
    Güncel veritabanını diske kaydeder ve döner.
    """

    if os.path.exists(persist_path):
        print(f"[i] Kayıtlı FAISS veritabanı bulundu, yükleniyor: {persist_path}")

        # Var olan veritabanı yükleniyor ve embedding_model ile isleniyor.
        vector_store = FAISS.load_local(persist_path, embedding_model, allow_dangerous_deserialization=True)

        # Mevcut veritabanındaki belgelerin hash'leri toplanıyor
        existing_hashes = get_existing_hashes(vector_store)
    else: 

        # Yeni FAISS index oluşturuluyor
        print("[i] FAISS veritabanı bulunamadı, yeni oluşturuluyor...")

        # Embedding boyutunu belirlemek için örnek sorgu embed ediliyor
        embedding_dim = len(embedding_model.embed_query("deneme 123"))
        # FAISS index (Inner Product tabanlı) oluşturuluyor
        index = faiss.IndexFlatIP(embedding_dim)

         # Boş bir FAISS veritabanı
        vector_store = FAISS(
            embedding_function=embedding_model,     # Embedding (gömme) fonksiyonu: metni vektöre çeviren model
            index=index,                           # FAISS'in vektörleri sakladığı ve sorguladığı ana yapı (index)
            docstore=InMemoryDocstore(),          # Belgeleri (dokümanları) hafızada tutan depo (anahtar-değer yapısı)
            index_to_docstore_id={}                # FAISS index ile docstore arasındaki id eşlemesi (boş başlatılıyor)
        )

    
        existing_hashes = set() # Henüz kayıtlı belge yok

    # Belgeleri daha küçük parçalara bölmek için text splitter tanımlanıyor
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    # Belgeler chunk'lara bölünüyor
    all_splits = text_splitter.split_documents(docs)


    # Her parçaya hash değeri atanıyor, yoksa hesaplanıyor
    for split in all_splits:
        if "hash" not in split.metadata:
            split.metadata["hash"] = compute_hash(split.page_content)
    
    # Daha önce veritabanında olmayan, yani yeni parçalar filtreleniyor
    new_docs = [doc for doc in all_splits if doc.metadata["hash"] not in existing_hashes]

    if new_docs: 
        print(f"[+] {len(new_docs)} yeni belge bulundu, veritabani guncelleniyor...")
        vector_store.add_documents(new_docs)
        # Güncellenmiş veritabanı diske kaydediliyor
        vector_store.save_local(persist_path)
    else:
        print("[i] Yeni belge yok, guncelleme yapilmadi.")
    return vector_store