import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from openai_clients import embedding_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os 
from load_docs import compute_hash
import time

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



def build_store(docs, persist_path='vector_db', batch_size=250):
    """
    FAISS vektör veritabanını oluşturur veya var olanı yükler.
    Yeni belgeleri hash ile kontrol eder, embeddingleri batch halinde ekler.
    Her aşama loglanır ve süreleri ölçülür.
    """

    total_start = time.time()

    # 1. FAISS veritabanı yükleniyor veya oluşturuluyor
    if os.path.exists(persist_path):
        print(f"[i] Kayıtlı FAISS veritabanı bulundu, yükleniyor: {persist_path}")
        vector_store = FAISS.load_local(persist_path, embedding_model, allow_dangerous_deserialization=True)
        existing_hashes = get_existing_hashes(vector_store)
    else:
        print("[i] FAISS veritabanı bulunamadı, yeni oluşturuluyor...")
        embedding_dim = len(embedding_model.embed_query("deneme123"))
        index = faiss.IndexFlatIP(embedding_dim)
        vector_store = FAISS(
            embedding_function=embedding_model,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={}
        )
        existing_hashes = set()

    # 2. Belgeleri küçük parçalara bölüyoruz
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)

    for split in all_splits:
        if "hash" not in split.metadata:
            split.metadata["hash"] = compute_hash(split.page_content)

    new_docs = [doc for doc in all_splits if doc.metadata["hash"] not in existing_hashes]

    if not new_docs:
        print("[i] Yeni belge yok, güncelleme yapılmadı.")
        return vector_store

    print(f"[+] {len(new_docs)} yeni belge bulundu, veritabanı güncelleniyor...")

    # 3. Batch halinde embedding
    embed_start = time.time()
    for i in range(0, len(new_docs), batch_size):
        batch = new_docs[i:i+batch_size]
        print(f"  ↪️ Batch {i}-{i+len(batch)} embedleniyor...")
        batch_start = time.time()
        vector_store.add_documents(batch)
        batch_end = time.time()
        print(f"    ⏱️ Batch süresi: {batch_end - batch_start:.2f} sn")

    embed_end = time.time()
    print(f"[✓] Tüm embedding işlemi tamamlandı ({embed_end - embed_start:.2f} sn)")

    # 4. Veritabanını kaydet
    vector_store.save_local(persist_path)
    print(f"[✓] FAISS veritabanı kaydedildi → {persist_path}")

    total_end = time.time()
    print(f"[✓] build_store toplam süre: {total_end - total_start:.2f} sn")

    return vector_store