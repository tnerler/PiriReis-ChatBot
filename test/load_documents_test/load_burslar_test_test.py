from langchain.schema import Document
import hashlib
from typing import List
from datetime import datetime

def compute_hash(content: str) -> str:
    """İçeriğin benzersiz hash değerini hesaplar."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Burs ve indirim bilgileri JSON verisini işleyerek Document nesneleri oluşturur.
    """
    documents = []
    current_date = "2025-07-25 08:29:16"
    user_login = "tnerler"
    
    doc_title = data.get("document_title", "")
    metadata = data.get("metadata", {})
    university_name = metadata.get("university_name", "Piri Reis Üniversitesi")
    
    # Ana doküman oluştur
    full_content = f"# {doc_title}\n\n"
    
    for category in data.get("scholarship_categories", []):
        category_name = category.get("category_name", "")
        scholarships = category.get("scholarships", [])
        
        full_content += f"## {category_name}\n\n"
        
        # Kategori içeriği oluştur
        category_content = f"# {university_name} - {category_name}\n\n"
        
        for scholarship in scholarships:
            name = scholarship.get("name", "")
            description = scholarship.get("description", "")
            eligibility = scholarship.get("eligibility", "")
            
            full_content += f"### {name}\n\n{description}\n\n"
            full_content += f"**Kimler Yararlanabilir:** {eligibility}\n\n"
            
            category_content += f"## {name}\n\n{description}\n\n"
            category_content += f"**Kimler Yararlanabilir:** {eligibility}\n\n"
            
            # Koşul bilgisi varsa ekle
            if "condition" in scholarship:
                condition = scholarship.get("condition", "")
                full_content += f"**Burs/İndirim Koşulu:** {condition}\n\n"
                category_content += f"**Burs/İndirim Koşulu:** {condition}\n\n"
            
            # İndirim oranı bilgisi varsa ekle
            if "discount_rate" in scholarship:
                discount = scholarship.get("discount_rate", "")
                full_content += f"**İndirim Oranı:** {discount}%\n\n"
                category_content += f"**İndirim Oranı:** {discount}%\n\n"
            
            # Her burs için ayrı doküman oluştur
            scholarship_content = f"# {name}\n\n"
            scholarship_content += f"{description}\n\n"
            scholarship_content += f"**Burs/İndirim Kategorisi:** {category_name}\n"
            scholarship_content += f"**Kimler Yararlanabilir:** {eligibility}\n"
            
            if "condition" in scholarship:
                scholarship_content += f"**Burs/İndirim Koşulu:** {scholarship.get('condition', '')}\n"
            
            if "discount_rate" in scholarship:
                scholarship_content += f"**İndirim Oranı:** {scholarship.get('discount_rate', '')}%\n"
            
            if "type" in scholarship:
                scholarship_content += f"**Tür:** {scholarship.get('type', '')}\n"
                
            # Burs/indirim dokümanı ekle
            scholarship_hash = compute_hash(scholarship_content)
            documents.append(Document(
                page_content=scholarship_content,
                metadata={
                    "hash": scholarship_hash,
                    "title": f"{name} - {university_name}",
                    "university": university_name,
                    "category": category_name,
                    "scholarship_name": name,
                    "source": source_file,
                    "document_type": "burs_detay",
                    "processed_date": current_date,
                    "processed_by": user_login
                }
            ))
        
        # Kategori dokümanı ekle
        category_hash = compute_hash(category_content)
        documents.append(Document(
            page_content=category_content,
            metadata={
                "hash": category_hash,
                "title": f"{university_name} - {category_name}",
                "university": university_name,
                "category": category_name,
                "source": source_file,
                "document_type": "burs_kategori",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Özetli doküman ekle
    full_content += "\n## Burs ve İndirimlerin Genel Özeti\n\n"
    full_content += "| Burs/İndirim Adı | Kategori | İndirim Oranı | Kimler Yararlanabilir |\n"
    full_content += "|------------------|----------|--------------|----------------------|\n"
    
    for category in data.get("scholarship_categories", []):
        category_name = category.get("category_name", "")
        
        for scholarship in category.get("scholarships", []):
            name = scholarship.get("name", "")
            discount = scholarship.get("discount_rate", "-")
            eligibility = scholarship.get("eligibility", "").split(".")[0]
            
            full_content += f"| {name} | {category_name} | {discount} | {eligibility} |\n"
    
    # Not bilgisini ekle
    if "notes" in metadata:
        full_content += f"\n**Not:** {metadata['notes']}\n"
    
    # Ana dokümanı ekle
    full_hash = compute_hash(full_content)
    documents.append(Document(
        page_content=full_content,
        metadata={
            "hash": full_hash,
            "title": doc_title,
            "university": university_name,
            "source": source_file,
            "document_type": "burs_tam",
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    # Burs türlerine göre rehber dokümanları
    burs_turleri = {
        "öğrenim_bursu": ["ÖSYM-YKS Yerleştirme Bursu"],
        "nakit_destek": ["YKS Başarı Sıralaması Bursu"],
        "ozel_indirim": ["Kardeş İndirimi", "Engelsiz Eğitim İndirimi", "Gazi-Şehit İndirimi"],
        "denizcilik_indirimleri": ["Kız Öğrenci İndirimi", "Denizcilik Lisesi Mezunu İndirimi", "Uzun Dönem Staj İndirimi"]
    }
    
    for burs_turu, burs_isimleri in burs_turleri.items():
        tur_content = f"# {university_name} - {burs_turu.replace('_', ' ').title()} Rehberi\n\n"
        
        # İlgili bursları bul
        for category in data.get("scholarship_categories", []):
            for scholarship in category.get("scholarships", []):
                name = scholarship.get("name", "")
                
                if name in burs_isimleri:
                    description = scholarship.get("description", "")
                    eligibility = scholarship.get("eligibility", "")
                    
                    tur_content += f"## {name}\n\n{description}\n\n"
                    tur_content += f"**Kimler Yararlanabilir:** {eligibility}\n\n"
                    
                    if "condition" in scholarship:
                        tur_content += f"**Burs/İndirim Koşulu:** {scholarship.get('condition', '')}\n\n"
                    
                    if "discount_rate" in scholarship:
                        tur_content += f"**İndirim Oranı:** {scholarship.get('discount_rate', '')}%\n\n"
        
        # Türe göre doküman ekle
        if len(tur_content) > 100:  # Yeterli içerik varsa
            tur_hash = compute_hash(tur_content)
            documents.append(Document(
                page_content=tur_content,
                metadata={
                    "hash": tur_hash,
                    "title": f"{university_name} - {burs_turu.replace('_', ' ').title()} Rehberi",
                    "university": university_name,
                    "burs_turu": burs_turu,
                    "source": source_file,
                    "document_type": "burs_rehber",
                    "processed_date": current_date,
                    "processed_by": user_login
                }
            ))
    
    return documents