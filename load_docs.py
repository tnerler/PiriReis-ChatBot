import json
from langchain.schema import Document
import hashlib


def compute_hash(content: str) -> str:
    """
    Aynı içerik tekrar yüklenmesin diye içerikten SHA256 hash üretir.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def bilgiyi_al(item):
    
    context = item.get("context", "")

    if isinstance(context, list):
        return "\n".join(context)
    elif isinstance(context, str):
        return context.strip()
    else:
        return ""

    
    


def load_docs():
    """
    main_data.json dosyasını okuyarak LangChain Document listesi döner.
    """
    docs = []

    processed_hashes = set()

    try:
        with open("get_data/main_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"[DEBUG] main_data.json'dan {len(data)} item yüklendi")

        for item in data:
            text = bilgiyi_al(item).strip()
            text = " ".join(text.split())

            if not text:
                continue

            doc_hash = compute_hash(text)
            if doc_hash in processed_hashes:
                continue
            processed_hashes.add(doc_hash)

            metadata = {
                "hash": doc_hash,
                "type": item.get("type", ""),
                "source": "main_data.json"
            }
            docs.append(Document(
                page_content=text,
                metadata=metadata,
            ))


    except FileNotFoundError:
        print("❌ main_data.json bulunamadı.")
    except Exception as e:
        print(f"❌ main_data.json yüklenirken hata: {e}")



    print(f"[i] Toplam {len(docs)} unique document yüklendi")
    return docs
