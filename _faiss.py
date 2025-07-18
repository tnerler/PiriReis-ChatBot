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
    hashes = set()
    
    # vector_store içindeki tüm belgeleri tek tek dolaşacağız.
    for doc in vector_store.docstore._dict.values():
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
    if os.path.exists(persist_path):
        print(f"[i] Kayıtlı FAISS veritabanı bulundu, yükleniyor: {persist_path}")
        vector_store = FAISS.load_local(persist_path, embedding_model, allow_dangerous_deserialization=True)
        existing_hashes = get_existing_hashes(vector_store)
    
    else:
        print(f"[i] FAISS veritabanı bulunamadı, yeni oluşturuluyor...")
        embedding_dim = len(embedding_model.embed_query("deneme123"))
        index = faiss.IndexFlatIP(embedding_dim)
        vector_store = FAISS(
            embedding_function=embedding_model,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        existing_hashes = set()


        print(f"[i] Chunking başlatılıyor...")
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        all_splits = text_splitter.split_documents(docs)

        print(f"[i] Toplam {len(all_splits)} adet chunk oluşturuldu.")


        processed_docs = []
        skipped = 0
        start_time = time.time()


        for split in all_splits:
            chunk_hash = compute_hash(split.page_content)

            if chunk_hash in existing_hashes:
                skipped += 1 
                continue
        
            split.metadata["hash"] = chunk_hash
            processed_docs.append(split)
            
        print(f"[i] Yeni eklenecek döküman sayısı: {len(processed_docs)}, zaten var olan döküman sayısı {skipped}")

        # Batch ile ekleme
        for i in range(0, len(processed_docs), batch_size):
            batch = processed_docs[i:i+batch_size]
            print(f"[i] Embedding batch {i} → {i+len(batch)} arası...")
            vector_store.add_documents(batch)
        
        vector_store.save_local(persist_path)
        duration = round(time.time() - start_time, 2)
        print(f"[✓] FAISS veritabanı güncellendi. Süre: {duration} saniye")
    return vector_store