import faiss
from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.vectorstores import FAISS
from openai_clients import embeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os 
from load_docs import compute_hash


def get_existing_hashes(vector_store) -> set:

    """
    Var olan FAISS veritabanındaki tüm belgelerin hash değerlerini toplar.
    Böylece yeni belge eklerken aynı olanları eklemekten kaçınabiliriz.
    """

    hashes = set()
    for doc in vector_store.docstore._dict.values():
        doc_hash = doc.metadata.get("hash")
        if doc_hash:
            hashes.add(doc_hash)
    return hashes



def build_store(docs, persist_path='vector_db') : 

    """
    Belgeleri alır ve FAISS veritabanını oluşturur veya yükler.
    
    Eğer daha önce kaydedilmiş bir veritabanı varsa onu yükler.
    Yoksa yeni bir FAISS veritabanı oluşturur ve belgelerin embeddinglerini hesaplayarak ekler.
    
    datayi_guncelle=True olursa, yeni belgeleri mevcut veritabanına ekler.
    Bu eklemede belge tekrarlarını önlemek için hash kontrolü yapılır.
    
    Sonuçta güncel veya yeni FAISS veritabanını döner.
    """

    if os.path.exists(persist_path):
        print(f"[i] Kayıtlı FAISS veritabanı bulundu, yükleniyor: {persist_path}")
        vector_store = FAISS.load_local(persist_path, embeddings, allow_dangerous_deserialization=True)
        existing_hashes = get_existing_hashes(vector_store)
    else: 

        # Yeni FAISS index oluşturuluyor
        print("[i] FAISS veritabanı bulunamadı, yeni oluşturuluyor...")
        embedding_dim = len(embeddings.embed_query("deneme 123"))
        index = faiss.IndexFlatIP(embedding_dim)

        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={}
        )
    
        existing_hashes = set()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    all_splits = text_splitter.split_documents(docs)

    for split in all_splits:
        if "hash" not in split.metadata:
            split.metadata["hash"] = compute_hash(split.page_content)
    
    new_docs = [doc for doc in all_splits if doc.metadata["hash"] not in existing_hashes]
    if new_docs: 
        print(f"[+] {len(new_docs)} yeni belge bulundu, veritabani guncelleniyor...")
        vector_store.add_documents(new_docs)
        vector_store.save_local(persist_path)
    else:
        print("[i] Yeni belge yok, guncelleme yapilmadi.")
    return vector_store