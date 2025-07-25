import json
from langchain.schema import Document
import hashlib
import re


def compute_hash(content: str) -> str:
    """
    Aynı içerik tekrar yüklenmesin diye içerikten SHA256 hash üretir.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def bilgiyi_al(item):
    """
    JSON item içeriğini metin olarak döner.
    'context' varsa onu alır, yoksa 'soru' + 'cevap' birleştirir.
    """
    if "context" in item:
        context = item["context"]
        if isinstance(context, list):
            return "\n".join(context)
        elif isinstance(context, str):
            return context.strip()
    elif "soru-cevap" in item:
        return f"Soru: {item['soru'].strip()}\nCevap: {item['cevap'].strip()}"
    return ""


def extract_ranking_metadata(content):
    """
    İçerikten sıralama ve puan bilgilerini çıkarır.
    """
    metadata = {}
    
    # Taban/Tavan Başarı Sırası (Ranking ranges)
    taban_siralama_match = re.search(r'Taban Başarı Sırası:\s*(\d+)', content)
    tavan_siralama_match = re.search(r'Tavan Başarı Sırası:\s*(\d+)', content)
    
    if taban_siralama_match and tavan_siralama_match:
        metadata['taban_siralama'] = int(taban_siralama_match.group(1))
        metadata['tavan_siralama'] = int(tavan_siralama_match.group(1))
    
    # Taban/Tavan Puanı (Score ranges)
    taban_puan_match = re.search(r'Taban Puanı:\s*([\d.]+)', content)
    tavan_puan_match = re.search(r'Tavan Puanı:\s*([\d.]+)', content)
    
    if taban_puan_match and tavan_puan_match:
        metadata['taban_puan'] = float(taban_puan_match.group(1))
        metadata['tavan_puan'] = float(tavan_puan_match.group(1))
    
    # Program adı
    program_match = re.search(r'Program:\s*(.+?)(?:\n|$)', content)
    if program_match:
        metadata['program'] = program_match.group(1).strip()
    
    # Burs durumu
    burs_match = re.search(r'Burs Durumu:\s*(.+?)(?:\n|$)', content)
    if burs_match:
        metadata['burs_durumu'] = burs_match.group(1).strip()
    
    # Fakülte
    fakulte_match = re.search(r'Fakülte:\s*(.+?)(?:\n|$)', content)
    if fakulte_match:
        metadata['fakulte'] = fakulte_match.group(1).strip()
    
    return metadata


def create_ranking_query_docs(docs):
    """
    Sıralama sorguları için özel dokümanlar oluşturur.
    """
    ranking_docs = []
    
    # Sıralama belgelerini topla
    ranking_items = []
    for doc in docs:
        if 'taban_siralama' in doc.metadata and 'tavan_siralama' in doc.metadata:
            ranking_items.append(doc)
    
    # Sık sorulan sorular için özel dokümanlar oluştur
    if ranking_items:
        # Genel sıralama bilgisi dokümanu
        ranking_summary = "Piri Reis Üniversitesi Sıralama ve Puan Bilgileri:\n\n"
        for doc in ranking_items[:10]:  # İlk 10 bölüm için
            program = doc.metadata.get('program', '')
            burs = doc.metadata.get('burs_durumu', '')
            taban_siralama = doc.metadata.get('taban_siralama', '')
            tavan_siralama = doc.metadata.get('tavan_siralama', '')
            
            ranking_summary += f"{program} ({burs}): {tavan_siralama}-{taban_siralama} sıralama aralığı\n"
        
        ranking_summary += "\nSıralamaya göre bölüm seçimi için detaylı bilgi almak istiyorsanız, sıralamanızı belirtiniz."
        
        summary_doc = Document(
            page_content=ranking_summary,
            metadata={
                "hash": compute_hash(ranking_summary),
                "type": "siralama_ozeti",
                "source": "generated",
                "query_type": "ranking_summary"
            }
        )
        ranking_docs.append(summary_doc)
        
        # Ortak soru formatları için dokümanlar
        common_queries = [
            "Sıralamam ile hangi bölümlere girebilirim?",
            "Bu sıralama ile kabul olan bölümler hangileri?",
            "Sıralaması yeten bölümler listesi",
            "Puan ve sıralama ile bölüm seçimi"
        ]
        
        for query in common_queries:
            query_content = f"{query}\n\nPiri Reis Üniversitesi'nde sıralamanıza uygun bölümleri öğrenmek için sıralamanızı belirtiniz. Üniversitemizde farklı burs türlerinde (tam burslu, %50 burslu, ücretli) çeşitli bölümler bulunmaktadır."
            
            query_doc = Document(
                page_content=query_content,
                metadata={
                    "hash": compute_hash(query_content),
                    "type": "siralama_sorgu",
                    "source": "generated",
                    "query_type": "ranking_query"
                }
            )
            ranking_docs.append(query_doc)
    
    return ranking_docs


    
    


def load_docs():
    """
    main_data.json dosyasını okuyarak LangChain Document listesi döner.
    Sıralama ve puan bilgileri için özelleştirilmiş metadata ekler.
    """
    docs = []

    processed_hashes = set()

    try:
        with open("get_data/main_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"[DEBUG] main_data.json'dan {len(data)} item yüklendi")

        for item in data:
            text = f"{item.get('type', '')}: {bilgiyi_al(item).strip()}"
            text = " ".join(text.split())

            if not text:
                continue

            doc_hash = compute_hash(text)
            if doc_hash in processed_hashes:
                continue
            processed_hashes.add(doc_hash)

            # Temel metadata
            metadata = {
                "hash": doc_hash,
                "type": item.get("type", ""),
                "source": "main_data.json"
            }
            
            # Sıralama ve puan bilgilerini çıkar
            content = bilgiyi_al(item)
            ranking_metadata = extract_ranking_metadata(content)
            metadata.update(ranking_metadata)
            
            # Sıralama dokümanı olup olmadığını işaretle
            if 'Sıralamaları ve Puanları' in item.get('type', ''):
                metadata['is_ranking_doc'] = True
                
                # Sıralama dokümanı için ek açıklayıcı metin ekle
                enhanced_text = text
                if 'taban_siralama' in metadata and 'tavan_siralama' in metadata:
                    siralama_aciklama = f"\n\nBu bölüme {metadata['tavan_siralama']} ile {metadata['taban_siralama']} arasındaki sıralamaya sahip öğrenciler girebilir."
                    enhanced_text += siralama_aciklama
                    
                text = enhanced_text

            docs.append(Document(
                page_content=text,
                metadata=metadata,
            ))

    except FileNotFoundError:
        print("❌ main_data.json bulunamadı.")
    except Exception as e:
        print(f"❌ main_data.json yüklenirken hata: {e}")

    # Sıralama sorguları için özel dokümanlar ekle
    ranking_docs = create_ranking_query_docs(docs)
    docs.extend(ranking_docs)

    print(f"[i] Toplam {len(docs)} unique document yüklendi ({len(ranking_docs)} özel sıralama dokümanı dahil)")
    return docs
