import os
import pickle
import hashlib
from openai_clients import embedding_model
from load_docs import load_docs
from _faiss import compute_hash

cache_folder = "tag_embeddings"
cache_path = os.path.join(cache_folder, "tag_embeddings_cache.pkl")
os.makedirs(cache_folder, exist_ok=True)


def update_and_get_tag_embeddings():
    """
    Tag embedding cache'ini günceller ve güncellenmiş haliyle geri döner.
    """

    # Cache yükle
    if os.path.exists(cache_path):
        with open(cache_path, "rb") as f:
            tag_embeddings_with_hash = pickle.load(f)
    else:
        tag_embeddings_with_hash = {}

    docs = load_docs()
    unique_tags = set()

    for doc in docs:
        # LangChain Document metadata
        if hasattr(doc, 'metadata') and 'tags' in doc.metadata:
            tags = doc.metadata['tags']
            if isinstance(tags, list):
                unique_tags.update(t.strip() for t in tags if isinstance(t, str) and t.strip())

        # dict veri tipi
        if isinstance(doc, dict) and 'tags' in doc:
            tags = doc['tags']
            if isinstance(tags, list):
                unique_tags.update(t.strip() for t in tags if isinstance(t, str) and t.strip())

        # page_content içinde JSON varsa
        if hasattr(doc, 'page_content'):
            try:
                import json
                content = doc.page_content.strip()
                if content.startswith('{') or content.startswith('['):
                    json_data = json.loads(content)

                    if isinstance(json_data, dict) and 'tags' in json_data:
                        tags = json_data['tags']
                        if isinstance(tags, list):
                            unique_tags.update(t.strip() for t in tags if isinstance(t, str) and t.strip())

                    elif isinstance(json_data, list):
                        for item in json_data:
                            if isinstance(item, dict) and 'tags' in item:
                                tags = item['tags']
                                if isinstance(tags, list):
                                    unique_tags.update(t.strip() for t in tags if isinstance(t, str) and t.strip())

            except Exception:
                pass  # parse hatası varsa sessiz geç

        # metadata içinde pages > items > tags varsa
        if hasattr(doc, 'metadata') and 'pages' in doc.metadata:
            pages_data = doc.metadata['pages']
            if isinstance(pages_data, list):
                for page in pages_data:
                    if isinstance(page, dict) and 'items' in page:
                        for item in page['items']:
                            if isinstance(item, dict) and 'tags' in item:
                                tags = item['tags']
                                if isinstance(tags, list):
                                    unique_tags.update(t.strip() for t in tags if isinstance(t, str) and t.strip())

    print(f"[i] {len(unique_tags)} adet benzersiz tag bulundu.")

    updated = False

    for tag in unique_tags:
        current_hash = compute_hash(tag)
        if tag in tag_embeddings_with_hash and tag_embeddings_with_hash[tag]["hash"] == current_hash:
            continue  # Güncel

        embedding = embedding_model.embed_query(tag)
        tag_embeddings_with_hash[tag] = {
            "hash": current_hash,
            "embedding": embedding
        }
        updated = True

    if updated:
        with open(cache_path, "wb") as f:
            pickle.dump(tag_embeddings_with_hash, f)
        print(f"[+] Tag embedding cache güncellendi. Toplam {len(tag_embeddings_with_hash)} tag kayıtlı.")
    else:
        print("[i] Tag embedding cache zaten güncel.")

    return tag_embeddings_with_hash
