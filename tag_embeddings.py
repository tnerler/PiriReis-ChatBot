import os 
import pickle 
import hashlib
from openai_clients import embedding_model
from load_docs import load_docs
from _faiss import compute_hash

cache_folder = "tag_embeddings"
cache_path = os.path.join(cache_folder, "tag_embeddings_cache.pkl")
os.makedirs(cache_folder, exist_ok=True)  # ✅ klasörü oluştur, varsa sorun yok


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

    # Dokümanlardaki tüm value alanlarını bir set içinde topla (tekrarsız)
    unique_values = set()
    
    print(f"[DEBUG] Toplam doc sayısı: {len(docs)}")
    
    for i, doc in enumerate(docs):
        print(f"[DEBUG] Doc {i}: type={type(doc)}")
        
        # Her türlü veri yapısını kontrol et
        if hasattr(doc, 'page_content'):
            print(f"[DEBUG] Doc {i} page_content var, uzunluk: {len(doc.page_content)}")
            try:
                import json
                json_data = json.loads(doc.page_content)
                print(f"[DEBUG] Doc {i} JSON parse başarılı, keys: {list(json_data.keys())}")
                
                if 'pages' in json_data:
                    print(f"[DEBUG] Doc {i} pages bulundu, sayı: {len(json_data['pages'])}")
                    for page_idx, page in enumerate(json_data['pages']):
                        if 'items' in page:
                            items = page['items']
                            print(f"[DEBUG] Page {page_idx} items sayısı: {len(items)}")
                            for item in items:
                                if 'value' in item:
                                    value = item['value'].strip()
                                    if value:
                                        unique_values.add(value)
                                        if len(unique_values) <= 5:  # İlk 5 value'yu göster
                                            print(f"[DEBUG] Value eklendi: {value[:50]}...")
                            
            except Exception as e:
                print(f"[DEBUG] Doc {i} JSON parse hatası: {e}")
                print(f"[DEBUG] Doc {i} page_content ilk 100 char: {doc.page_content[:100]}")
        
        if hasattr(doc, 'metadata'):
            print(f"[DEBUG] Doc {i} metadata keys: {list(doc.metadata.keys())}")
            metadata = doc.metadata
            
            # Metadata'da direkt pages varsa
            if 'pages' in metadata:
                pages_data = metadata['pages']
                print(f"[DEBUG] Doc {i} metadata'da pages bulundu, tip: {type(pages_data)}")
                if isinstance(pages_data, list):
                    for page in pages_data:
                        if 'items' in page:
                            items = page['items']
                            for item in items:
                                if 'value' in item:
                                    value = item['value'].strip()
                                    if value:
                                        unique_values.add(value)
            
            # Metadata'da direkt items varsa
            elif 'items' in metadata:
                items = metadata['items']
                print(f"[DEBUG] Doc {i} metadata'da items bulundu, sayı: {len(items)}")
                for item in items:
                    if 'value' in item:
                        value = item['value'].strip()
                        if value:
                            unique_values.add(value)
        
        # Dict ise
        if isinstance(doc, dict):
            print(f"[DEBUG] Doc {i} dict, keys: {list(doc.keys())}")
            if 'pages' in doc:
                for page in doc['pages']:
                    if 'items' in page:
                        items = page['items']
                        for item in items:
                            if 'value' in item:
                                value = item['value'].strip()
                                if value:
                                    unique_values.add(value)
    
    print(f"[DEBUG] TOPLAM benzersiz value sayısı: {len(unique_values)}")
    if len(unique_values) > 0:
        print(f"[DEBUG] İlk birkaç value: {list(unique_values)[:5]}")

    updated = False  # Güncelleme yapıldı mı kontrol etmek için

    # Her benzersiz tag için işlem yap
    for tag in unique_values:
        current_hash = compute_hash(tag)  # Tag'ın güncel hash'i hesapla

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
        updated = True  # Guncelleme yapildi flag

    # Eğer güncelleme yapılmışsa cache dosyasını diske kaydet
    if updated:
        with open(cache_path, "wb") as f:
            pickle.dump(tag_embeddings_with_hash, f)
        print("[+] Tag embedding cache güncellendi.")
    else:
        print("[i] Tag embedding cache zaten güncel.")

    return tag_embeddings_with_hash