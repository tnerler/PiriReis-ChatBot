import json
from langchain.schema import Document
import hashlib


def compute_hash(content: str) -> str:
    """
    Aynı içerik tekrar yüklenmesin diye içerikten SHA256 hash üretir.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def soru_cevap(item) : 
    content = f"Soru: {item['soru']}\nCevap: {item['cevap']}"
    return content



def bilgi(item) : 
    content=f"Bilgi: {item['context']}"
    return content



def universite_kadrosu(item): 
    content = "Üniversite Kadrosu:\n\n" + "\n".join(item["context"])
    return content


def duyurular(item):
    return f"Duyuru: {item['title']}\nLink: {item['link']}"


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
    
    if "departments" in item:
        return "\n".join(
            f"Bölüm: {d.get('name', '')} - Link: {d.get('link', '')}"
            for d in item.get("departments", [])
        )
    
    return json.dumps(item, indent=2)  # fallback metinleştirici

def load_docs():
    """
    main_data.json dosyasını okuyarak LangChain Document listesi döner.
    """
    docs = []

    try:
        with open("get_data/main_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("❌ main_data.json bulunamadı.")
        return docs

    for item in data:
        text = universal_parser(item)
        if not text.strip():
            continue

        doc_hash = compute_hash(text)
        tags = item.get("tags", [])
        
        docs.append(Document(
            page_content=text,
            metadata={
                "hash": doc_hash,
                "tags": tags,
                "type": item.get("type", "bilinmeyen")
            }
        ))

    return docs

