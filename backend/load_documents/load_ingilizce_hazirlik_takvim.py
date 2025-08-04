import json
from langchain.schema import Document
import hashlib
import os
from typing import List, Dict, Any
import glob

def process_data(data: dict, source_file: str) -> List[Document]:
    """
    İngilizce Hazırlık Akademik Takvim JSON verisini işleyerek Document nesneleri oluşturur.
    """
    documents = []
    current_date = "2025-07-31 07:45:03"
    user_login = "tnerler"
    
    doc_title = data.get("document_title", "İngilizce Hazırlık Akademik Takvim")
    metadata = data.get("metadata", {})
    university_name = metadata.get("university_name", "Piri Reis Üniversitesi")
    academic_year = metadata.get("academic_year", "")
    
    # Ana takvim dokümanı oluştur
    full_content = f"# {doc_title}\n\n"
    full_content += f"## {university_name} - {academic_year} Akademik Yılı\n\n"
    
    if "approval" in metadata:
        approval = metadata["approval"]
        full_content += f"*{approval.get('approved_by', '')} tarafından {approval.get('date', '')} tarih ve {approval.get('meeting_number', '')} sayılı toplantısında kabul edilmiştir.*\n\n"
    
    # Yarıyıl Öncesi Takvim
    pre_term = data.get("pre_term_calendar", {})
    pre_term_title = pre_term.get("title", "")
    pre_term_events = pre_term.get("events", [])
    
    if pre_term_title:
        full_content += f"## {pre_term_title}\n\n"
        
        for event in pre_term_events:
            event_name = event.get("name", "")
            event_date = event.get("date", "")
            event_desc = event.get("description", "")
            
            full_content += f"**{event_name}:** {event_date}\n"
            if event_desc:
                full_content += f"*{event_desc}*\n"
            full_content += "\n"
    
    # Yarıyıl ve Sınavlar Takvimi
    term_calendar = data.get("term_calendar", {})
    term_title = term_calendar.get("title", "")
    term_events = term_calendar.get("events", [])
    terms = term_calendar.get("terms", [])
    
    if term_title:
        full_content += f"## {term_title}\n\n"
        
        # Genel dönem etkinlikleri
        for event in term_events:
            event_name = event.get("name", "")
            event_date = event.get("date", "")
            full_content += f"**{event_name}:** {event_date}\n\n"
        
        # Dönemler
        for term in terms:
            term_name = term.get("name", "")
            term_date_range = term.get("date_range", "")
            term_events = term.get("events", [])
            
            full_content += f"### {term_name}\n"
            full_content += f"*{term_date_range}*\n\n"
            
            for event in term_events:
                event_name = event.get("name", "")
                event_date = event.get("date", "")
                full_content += f"**{event_name}:** {event_date}\n"
            
            full_content += "\n"
    
    # Notlar
    notes = data.get("notes", [])
    if notes:
        full_content += "## Önemli Notlar\n\n"
        for i, note in enumerate(notes, 1):
            full_content += f"{i}. {note}\n"
        full_content += "\n"
    
    # Ana doküman oluştur
    main_hash = compute_hash(full_content)
    documents.append(Document(
        page_content=full_content,
        metadata={
            "hash": main_hash,
            "title": f"{university_name} - {doc_title}",
            "university": university_name,
            "academic_year": academic_year,
            "document_type": "akademik_takvim",
            "source": source_file,
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    # Güz Dönemi dokümanı
    if terms and len(terms) > 0:
        guz_donem = terms[0]
        guz_content = f"# {university_name} - Güz Dönemi Akademik Takvim ({academic_year})\n\n"
        guz_content += f"## {guz_donem.get('name', '')}\n"
        guz_content += f"*{guz_donem.get('date_range', '')}*\n\n"
        
        for event in guz_donem.get("events", []):
            guz_content += f"**{event.get('name', '')}:** {event.get('date', '')}\n"
        
        guz_hash = compute_hash(guz_content)
        documents.append(Document(
            page_content=guz_content,
            metadata={
                "hash": guz_hash,
                "title": f"{university_name} - Güz Dönemi Akademik Takvim",
                "university": university_name,
                "academic_year": academic_year,
                "donem": "guz",
                "document_type": "akademik_takvim_donem",
                "source": source_file,
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Bahar Dönemi dokümanı
    if terms and len(terms) > 1:
        bahar_donem = terms[1]
        bahar_content = f"# {university_name} - Bahar Dönemi Akademik Takvim ({academic_year})\n\n"
        bahar_content += f"## {bahar_donem.get('name', '')}\n"
        bahar_content += f"*{bahar_donem.get('date_range', '')}*\n\n"
        
        for event in bahar_donem.get("events", []):
            bahar_content += f"**{event.get('name', '')}:** {event.get('date', '')}\n"
        
        bahar_hash = compute_hash(bahar_content)
        documents.append(Document(
            page_content=bahar_content,
            metadata={
                "hash": bahar_hash,
                "title": f"{university_name} - Bahar Dönemi Akademik Takvim",
                "university": university_name,
                "academic_year": academic_year,
                "donem": "bahar",
                "document_type": "akademik_takvim_donem",
                "source": source_file,
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Sınav Takvimi dokümanı
    sinav_content = f"# {university_name} - İngilizce Hazırlık Sınav Takvimi ({academic_year})\n\n"
    
    # Yarıyıl öncesi sınavlar
    sinav_content += "## Yarıyıl Öncesi Sınavlar\n\n"
    for event in pre_term_events:
        if "Sınav" in event.get("name", "") or "sınav" in event.get("name", "").lower():
            sinav_content += f"**{event.get('name', '')}:** {event.get('date', '')}\n"
    sinav_content += "\n"
    
    # Güz dönemi sınavları
    if terms and len(terms) > 0:
        sinav_content += "## Güz Dönemi Sınavları\n\n"
        for event in terms[0].get("events", []):
            if "Sınav" in event.get("name", "") or "sınav" in event.get("name", "").lower():
                sinav_content += f"**{event.get('name', '')}:** {event.get('date', '')}\n"
        sinav_content += "\n"
    
    # Bahar dönemi sınavları
    if terms and len(terms) > 1:
        sinav_content += "## Bahar Dönemi Sınavları\n\n"
        for event in terms[1].get("events", []):
            if "Sınav" in event.get("name", "") or "sınav" in event.get("name", "").lower():
                sinav_content += f"**{event.get('name', '')}:** {event.get('date', '')}\n"
        sinav_content += "\n"
    
    # Sınav notları
    sinav_content += "## Önemli Sınav Notları\n\n"
    for note in notes:
        if "sınav" in note.lower():
            sinav_content += f"- {note}\n"
    
    # Yeterince içerik varsa sınav dokümanını ekle
    if len(sinav_content) > 200:
        sinav_hash = compute_hash(sinav_content)
        documents.append(Document(
            page_content=sinav_content,
            metadata={
                "hash": sinav_hash,
                "title": f"{university_name} - İngilizce Hazırlık Sınav Takvimi",
                "university": university_name,
                "academic_year": academic_year,
                "document_type": "sinav_takvim",
                "source": source_file,
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    return documents

def compute_hash(content: str) -> str:
    """
    İçerik için bir hash değeri hesaplar.
    """
    import hashlib
    return hashlib.md5(content.encode()).hexdigest()