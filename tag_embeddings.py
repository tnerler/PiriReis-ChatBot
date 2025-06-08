import os 
import pickle 
import hashlib
from openai_clients import embedding_model
from load_docs import load_docs
from _faiss import compute_hash


cache_folder = "tag_embeddings"
cache_path = os.path.join(cache_folder, "tag_embeddings_cache.pkl")

"""
Öncelikle tag embeddinglerini saklamak için bir cache dosyası ve klasörü belirliyoruz.
Bu, her seferinde aynı tag'lerin embeddinglerini tekrar tekrar hesaplamamak için önemli.
"""


def update_and_get_tag_embeddings():
    """
    Tag embedding cache'ini günceller ve güncellenmiş haliyle geri döner.

    - Daha önceki cache varsa yükler.
    - Yeni eklenen dokümanlardaki tag'leri kontrol eder.
    - Yeni veya güncellenmiş tag'ler varsa embedding hesaplar.
    - Cache dosyasını günceller.
    - Sonuç olarak tüm embedding cache'ini return eder.
    """

    # Cache dosyası varsa yükle, yoksa boş dict oluştur
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            tag_embeddings_with_hash = pickle.load(f)
    else:
        tag_embeddings_with_hash = {}

    # Dokumanlari yukle
    docs = load_docs()

    # Dokümanlardaki tüm tag'leri bir set içinde topla (tekrarsız)
    unique_tags = set()
    for doc in docs:
        tags = doc.metadata.get("tags", [])
        unique_tags.update(tags)

    updated = False  # Güncelleme yapıldı mı kontrol etmek için

     # Her benzersiz tag için işlem yap
    for tag in unique_tags:

        current_hash = compute_hash(tag) # Tag'ın güncel hash'i hesapla

        # Cache'de varsa ve hash aynı ise, embedding yeniden hesaplanmaz
        if tag in tag_embeddings_with_hash:
            stored_hash = tag_embeddings_with_hash[tag]["hash"]
            if stored_hash == current_hash:
                continue  # Aynıysa geç

        # Hash değişmiş veya yeni tag ise embedding hesapla
        embedding = embedding_model.embed_query(tag)
        tag_embeddings_with_hash[tag] = {
            "hash": current_hash,
            "embedding": embedding
        }
        updated = True # Guncelleme yapildi flag


    # Eğer güncelleme yapılmışsa cache dosyasını diske kaydet
    if updated:
        with open(cache_path, "wb") as f:
            pickle.dump(tag_embeddings_with_hash, f)
        print("[+] Tag embedding cache güncellendi.")
    else:
        print("[i] Tag embedding cache zaten güncel.")

    return tag_embeddings_with_hash
