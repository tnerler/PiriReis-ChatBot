from langchain.schema import Document
import hashlib
from typing import List, Dict, Any
import json
from datetime import datetime

def compute_hash(content: str) -> str:
    """
    İçeriğin benzersiz bir hash değerini hesaplar.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Piri Reis Üniversitesi kampüs olanakları JSON verisini işleyerek 
    LangChain Document nesnelerine dönüştürür.
    
    Args:
        data: Yüklenen JSON verisi.
        source_file: Kaynak dosya adı.
        
    Returns:
        Document nesnelerinden oluşan bir liste.
    """
    documents = []
    current_date = "2025-07-25 07:34:29"  # UTC format
    user_login = "tnerler"
    
    # Ana bilgileri al
    doc_title = data.get("document_title", "")
    doc_url = data.get("document_url", "")
    contact_phone = data.get("contact_phone", "")
    metadata = data.get("metadata", {})
    university_name = metadata.get("university_name", "")
    
    # Tüm kampüs bilgilerini içeren ana metin oluştur
    full_content = f"{doc_title}\n\n"
    full_content += f"URL: {doc_url}\n"
    full_content += f"İletişim: {contact_phone}\n\n"
    
    # Bölümleri ekle
    for section in data.get("sections", []):
        section_title = section.get("section_title", "")
        full_content += f"# {section_title}\n\n"
        
        # Bölüm içeriğini ekle
        if "content" in section:
            if isinstance(section["content"], list):
                for paragraph in section["content"]:
                    full_content += f"{paragraph}\n\n"
            else:
                full_content += f"{section['content']}\n\n"
        
        # Özellikleri ekle
        if "features" in section:
            for feature in section["features"]:
                full_content += f"- {feature}\n"
            full_content += "\n"
    
    # Kampüs özellikleri bölümü
    campus_features = data.get("campus_features", {})
    if campus_features:
        full_content += "# Kampüs Özellikleri\n\n"
        
        # Konum bilgisi
        location = campus_features.get("location", {})
        if location:
            full_content += f"**Konum:** {location.get('city', '')}, {location.get('district', '')}\n"
            special_features = location.get("special_features", [])
            if special_features:
                full_content += f"**Özel Özellikler:** {', '.join(special_features)}\n"
        
        # Alan bilgisi
        if "area" in campus_features:
            full_content += f"**Alan:** {campus_features['area']}\n\n"
        
        # Tesisler
        facilities = campus_features.get("facilities", [])
        if facilities:
            full_content += "## Tesisler\n\n"
            for facility in facilities:
                full_content += f"**{facility.get('name', '')}:** {facility.get('description', '')}\n"
            full_content += "\n"
        
        # Tasarım özellikleri
        design_features = campus_features.get("design_features", [])
        if design_features:
            full_content += f"**Tasarım Özellikleri:** {', '.join(design_features)}\n\n"
    
    # Anahtar kelimeler
    keywords = data.get("keywords", [])
    if keywords:
        full_content += f"**Anahtar Kelimeler:** {', '.join(keywords)}\n"
    
    # Tam doküman için bir Document oluştur
    full_hash = compute_hash(full_content)
    documents.append(Document(
        page_content=full_content,
        metadata={
            "hash": full_hash,
            "title": doc_title,
            "university": university_name,
            "url": doc_url,
            "contact": contact_phone,
            "source": source_file,
            "document_type": "kampus_tam",
            "processed_date": current_date,
            "processed_by": user_login,
            "keywords": ", ".join(keywords)
        }
    ))
    
    # Her bölüm için ayrı bir doküman oluştur
    for section in data.get("sections", []):
        section_title = section.get("section_title", "")
        section_content = f"# {section_title}\n\n"
        
        # Bölüm içeriğini ekle
        if "content" in section:
            if isinstance(section["content"], list):
                for paragraph in section["content"]:
                    section_content += f"{paragraph}\n\n"
            else:
                section_content += f"{section['content']}\n\n"
        
        # Özellikleri ekle
        if "features" in section:
            for feature in section["features"]:
                section_content += f"- {feature}\n"
            section_content += "\n"
        
        # Bölüm bazlı doküman oluştur
        section_hash = compute_hash(section_content)
        documents.append(Document(
            page_content=section_content,
            metadata={
                "hash": section_hash,
                "title": f"{university_name} - {section_title}",
                "university": university_name,
                "url": f"{doc_url}#{section_title.lower().replace(' ', '-')}",
                "contact": contact_phone,
                "source": source_file,
                "document_type": "kampus_bolum",
                "section": section_title,
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Kampüs tesisleri hakkında ayrı bir doküman oluştur
    facilities = campus_features.get("facilities", [])
    if facilities:
        facilities_content = f"# {university_name} Kampüs Tesisleri\n\n"
        
        for facility in facilities:
            facility_name = facility.get("name", "")
            facility_desc = facility.get("description", "")
            facilities_content += f"## {facility_name}\n{facility_desc}\n\n"
        
        facilities_hash = compute_hash(facilities_content)
        documents.append(Document(
            page_content=facilities_content,
            metadata={
                "hash": facilities_hash,
                "title": f"{university_name} Kampüs Tesisleri",
                "university": university_name,
                "url": f"{doc_url}#tesisler",
                "contact": contact_phone,
                "source": source_file,
                "document_type": "kampus_tesisler",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Konum bilgisi için ayrı bir doküman oluştur
    location = campus_features.get("location", {})
    if location:
        location_content = f"# {university_name} Kampüs Konumu\n\n"
        location_content += f"Şehir: {location.get('city', '')}\n"
        location_content += f"İlçe: {location.get('district', '')}\n"
        
        special_features = location.get("special_features", [])
        if special_features:
            location_content += f"Özel Özellikler: {', '.join(special_features)}\n\n"
        
        area = campus_features.get("area", "")
        if area:
            location_content += f"Kampüs Alanı: {area}\n\n"
        
        location_hash = compute_hash(location_content)
        documents.append(Document(
            page_content=location_content,
            metadata={
                "hash": location_hash,
                "title": f"{university_name} Kampüs Konumu",
                "university": university_name,
                "url": f"{doc_url}#konum",
                "city": location.get("city", ""),
                "district": location.get("district", ""),
                "source": source_file,
                "document_type": "kampus_konum",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Her tesis türü için ayrı doküman oluştur
    facility_types = {}
    for facility in facilities:
        facility_name = facility.get("name", "")
        facility_desc = facility.get("description", "")
        
        facility_content = f"# {university_name} - {facility_name}\n\n"
        facility_content += f"{facility_desc}\n\n"
        facility_content += f"Kampüs: {location.get('city', '')}, {location.get('district', '')}\n"
        facility_content += f"İletişim: {contact_phone}\n"
        
        facility_hash = compute_hash(facility_content)
        documents.append(Document(
            page_content=facility_content,
            metadata={
                "hash": facility_hash,
                "title": f"{university_name} - {facility_name}",
                "university": university_name,
                "facility": facility_name,
                "url": f"{doc_url}#{facility_name.lower().replace(' ', '-')}",
                "contact": contact_phone,
                "source": source_file,
                "document_type": "kampus_tesis",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
        
        # Tesis türüne göre grupla
        if "Spor" in facility_name:
            if "spor_tesisleri" not in facility_types:
                facility_types["spor_tesisleri"] = []
            facility_types["spor_tesisleri"].append({
                "name": facility_name,
                "description": facility_desc
            })
        elif "Kütüphane" in facility_name:
            if "kutuphane" not in facility_types:
                facility_types["kutuphane"] = []
            facility_types["kutuphane"].append({
                "name": facility_name,
                "description": facility_desc
            })
        elif "Yemekhane" in facility_name or "Kafeterya" in facility_name:
            if "yeme_icme" not in facility_types:
                facility_types["yeme_icme"] = []
            facility_types["yeme_icme"].append({
                "name": facility_name,
                "description": facility_desc
            })
        elif "Sağlık" in facility_name:
            if "saglik" not in facility_types:
                facility_types["saglik"] = []
            facility_types["saglik"].append({
                "name": facility_name,
                "description": facility_desc
            })
        elif "Sosyal" in facility_name:
            if "sosyal" not in facility_types:
                facility_types["sosyal"] = []
            facility_types["sosyal"].append({
                "name": facility_name,
                "description": facility_desc
            })
    
    # Tesis türleri için dokümanlar oluştur
    for facility_type, facilities_list in facility_types.items():
        type_name = ""
        if facility_type == "spor_tesisleri":
            type_name = "Spor Tesisleri"
        elif facility_type == "kutuphane":
            type_name = "Kütüphane"
        elif facility_type == "yeme_icme":
            type_name = "Yeme-İçme Alanları"
        elif facility_type == "saglik":
            type_name = "Sağlık Hizmetleri"
        elif facility_type == "sosyal":
            type_name = "Sosyal Alanlar"
        
        if type_name:
            type_content = f"# {university_name} - {type_name}\n\n"
            
            for facility in facilities_list:
                type_content += f"## {facility['name']}\n"
                type_content += f"{facility['description']}\n\n"
            
            type_hash = compute_hash(type_content)
            documents.append(Document(
                page_content=type_content,
                metadata={
                    "hash": type_hash,
                    "title": f"{university_name} - {type_name}",
                    "university": university_name,
                    "facility_type": type_name,
                    "url": f"{doc_url}#{type_name.lower().replace(' ', '-')}",
                    "contact": contact_phone,
                    "source": source_file,
                    "document_type": f"kampus_{facility_type}",
                    "processed_date": current_date,
                    "processed_by": user_login
                }
            ))
    
    # Soru-cevap formatı için hazırlanmış doküman
    faq_content = f"# {university_name} Kampüs Hakkında Sıkça Sorulan Sorular\n\n"
    
    # Sorular ve cevapları ekle
    faq_content += "## Piri Reis Üniversitesi kampüsü nerededir?\n"
    faq_content += f"Piri Reis Üniversitesi kampüsü, {location.get('city', '')}'un {location.get('district', '')} ilçesinde, {', '.join(location.get('special_features', []))} {campus_features.get('area', '')} bir alan üzerinde kurulmuştur.\n\n"
    
    faq_content += "## Piri Reis Üniversitesi kampüsünde hangi tesisler bulunmaktadır?\n"
    facility_names = [facility.get('name', '') for facility in facilities]
    faq_content += f"Kampüsümüzde {', '.join(facility_names)} bulunmaktadır.\n\n"
    
    faq_content += "## Piri Reis Üniversitesi'nde ne tür sosyal etkinlikler düzenlenir?\n"
    faq_content += "Üniversitemizde öğrenci kulüpleri aracılığıyla çeşitli sosyal, kültürel ve sportif etkinlikler düzenlenmektedir.\n\n"
    
    faq_content += "## Piri Reis Üniversitesi kampüsünün özellikleri nelerdir?\n"
    design_features = campus_features.get("design_features", [])
    faq_content += f"Kampüsümüz {', '.join(design_features)} özellikleriyle öne çıkmaktadır.\n\n"
    
    faq_hash = compute_hash(faq_content)
    documents.append(Document(
        page_content=faq_content,
        metadata={
            "hash": faq_hash,
            "title": f"{university_name} Kampüs Sıkça Sorulan Sorular",
            "university": university_name,
            "url": f"{doc_url}#sss",
            "contact": contact_phone,
            "source": source_file,
            "document_type": "kampus_sss",
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    return documents