import json
from langchain.schema import Document
import hashlib


def compute_hash(content: str) -> str:
    """
    Aynı içerik tekrar yüklenmesin diye içerikten SHA256 hash üretir.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def universal_parser(item):
    """
    JSON'daki içeriği akıllı şekilde ayrıştırır.
    'soru-cevap', 'context', 'departments' gibi özel alanları tanır.
    Geri kalan durumlarda fallback olarak tüm objeyi JSON formatında düzleştirir.
    """
    t = item.get("type", "").lower()
    
    if t == "soru-cevap":
        return f"Soru: {item.get('soru', '')}\nCevap: {item.get('cevap', '')}"
    
    if "context" in item:
        context = item["context"]
        if isinstance(context, list):
            return "\n".join(context)
        return str(context)
    
    # pages yapısı varsa - sadece önemli text bilgileri al, tekrarları önle
    if "pages" in item:
        unique_texts = set()  # Tekrarları önlemek için set kullan
        
        for page in item["pages"]:
            # text, md ve items'daki value'ları kontrol et
            candidates = []
            
            if "text" in page and page["text"].strip():
                candidates.append(page["text"].strip())
            if "md" in page and page["md"].strip():
                candidates.append(page["md"].strip())
            if "items" in page:
                for page_item in page["items"]:
                    if "value" in page_item and page_item["value"].strip():
                        # Sadece text ve heading tiplerini al
                        item_type = page_item.get("type", "")
                        if item_type in ["text", "heading"]:
                            candidates.append(page_item["value"].strip())
            
            # Benzersiz olanları set'e ekle
            for candidate in candidates:
                if candidate:  # Boş değilse
                    unique_texts.add(candidate)
        
        return "\n".join(unique_texts)
    
    return json.dumps(item, indent=2, ensure_ascii=False)  # fallback metinleştirici


def load_docs():
    """
    main_data.json dosyasını okuyarak LangChain Document listesi döner.
    Ayrıca paste.txt dosyasındaki verileri de işler.
    """
    docs = []
    processed_hashes = set()  # Tekrar eden hash'leri engellemek için

    # main_data.json dosyasını yükle
    try:
        with open("get_data/main_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        print(f"[DEBUG] main_data.json'dan {len(data)} item yüklendi")
        
        for item in data:
            text = universal_parser(item).strip()
            text = " ".join(text.split())
            if not text.strip():
                continue

            doc_hash = compute_hash(text)
            
            # Tekrar eden hash'i atlayın
            if doc_hash in processed_hashes:
                continue
            processed_hashes.add(doc_hash)
            
            # Metadata'ya tags ekle
            metadata = {
                "hash": doc_hash,
                "type": item.get("type", "bilinmeyen"),
                "source": "main_data.json"
            }
            
            # Eğer tags varsa metadata'ya ekle
            if "tags" in item:
                metadata["tags"] = item["tags"]
            
            docs.append(Document(
                page_content=text,
                metadata=metadata
            ))
            
    except FileNotFoundError:
        print("❌ main_data.json bulunamadı.")
    except Exception as e:
        print(f"❌ main_data.json yüklenirken hata: {e}")

    # Başka dosyalar varsa buraya eklenebilir

    print(f"[DEBUG] Toplam {len(docs)} unique document yüklendi")
    return docs
