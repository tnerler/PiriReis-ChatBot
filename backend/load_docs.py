import json
from langchain.schema import Document
import hashlib
import os
from typing import List
import glob
from backend.json_processor_map import json_processor_map
from backend.load_documents.load_pru_brosur import process_data as process_pru_brosur_md

def compute_hash(content: str) -> str:
    """
    Computes a SHA256 hash from content to prevent duplicate document loading.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def load_docs() -> List[Document]:
    """
    Loads all JSON and relevant MD files in the data directory and converts them to LangChain Documents.
    Handles different JSON structures according to file name mapping.
    """
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(BASE_DIR, r"backend/get_data")

    # Get all JSON and MD files in the data directory
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    md_files = glob.glob(os.path.join(data_dir, "*.md"))

    all_docs = []
    processed_hashes = set()
    
    # --- JSON files ---
    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            file_name = os.path.basename(json_file).lower()
            print(f"[✓] Loaded {file_name}")

            processor = json_processor_map.get(file_name)
            if processor is None:
                print(f"[WARNING] Unknown JSON structure in {file_name}, skipping...")
                continue

            docs = processor(data, file_name)
            
            # Filter out duplicates based on content hash
            for doc in docs:
                if doc.metadata["hash"] not in processed_hashes:
                    processed_hashes.add(doc.metadata["hash"])
                    all_docs.append(doc)

        except FileNotFoundError:
            print(f"❌ {os.path.basename(json_file)} not found.")
        except json.JSONDecodeError:
            print(f"❌ Error decoding {os.path.basename(json_file)}: Invalid JSON format.")
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(json_file)}: {e}")

    # --- Markdown files ---
    for md_file in md_files:
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                md_content = f.read()
            
            file_name = os.path.basename(md_file)
            print(f"[✓] Loaded {file_name}")

            # Şimdilik sadece pru_brosur.md destekleniyor
            if "pru_brosur" in file_name.lower():
                docs = process_pru_brosur_md(md_content, file_name)
            else:
                # İleriki aşamada farklı markdown dosya tipleri için burada işleme eklenebilir
                print(f"[WARNING] Unknown MD file type {file_name}, skipping...")
                continue

            # Filter out duplicates based on content hash
            for doc in docs:
                if doc.metadata["hash"] not in processed_hashes:
                    processed_hashes.add(doc.metadata["hash"])
                    all_docs.append(doc)
                    
        except FileNotFoundError:
            print(f"❌ {os.path.basename(md_file)} not found.")
        except Exception as e:
            print(f"❌ Error processing {os.path.basename(md_file)}: {e}")
    
    print(f"[i] Total {len(all_docs)} unique documents loaded")
    return all_docs