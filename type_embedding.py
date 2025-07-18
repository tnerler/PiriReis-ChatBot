import pickle
import os

def save_embedding_cache(cache: dict, filepath: str):
    """Embedding cache'ini pkl dosyasına kaydeder."""
    with open(filepath, "wb") as f:
        pickle.dump(cache, f)
    print(f"[i] Embedding cache '{filepath}' dosyasına kaydedildi.")

def load_embedding_cache(filepath: str) -> dict:
    """Eğer varsa embedding cache pkl dosyasını yükler, yoksa boş dict döner."""
    if os.path.exists(filepath):
        with open(filepath, "rb") as f:
            cache = pickle.load(f)
        print(f"[i] Embedding cache '{filepath}' dosyasından yüklendi.")
        return cache
    else:
        print(f"[i] Embedding cache '{filepath}' bulunamadı, yeni oluşturuluyor.")
        return {}
