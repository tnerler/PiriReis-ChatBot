import json
from langchain.schema import Document
import hashlib
import os
from typing import List, Dict, Any
import glob

def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Lisans ve Önlisans Akademik Takvim JSON verisini işleyerek Document nesneleri oluşturur.
    """
    documents = []
    current_date = "2025-07-31 07:52:01"
    user_login = "tnerler"
    
    doc_title = data.get("document_title", "")
    metadata = data.get("metadata", {})
    university_name = metadata.get("university_name", "Piri Reis Üniversitesi")
    academic_year = metadata.get("academic_year", "")
    document_type = metadata.get("document_type", "")
    
    # Ana takvim dokümanı oluştur
    full_content = f"# {doc_title}\n\n"
    full_content += f"## {university_name} - {academic_year} {document_type}\n\n"
    
    if "approval" in metadata:
        approval = metadata["approval"]
        full_content += f"*{approval.get('approved_by', '')} tarafından {approval.get('date', '')} tarih ve {approval.get('meeting_number', '')} sayılı toplantısında kabul edilmiştir.*\n\n"
    
    # Akademik Takvim Etkinlikleri
    academic_calendar = data.get("academic_calendar", {})
    events = academic_calendar.get("events", [])
    
    full_content += "## Akademik Takvim\n\n"
    for event in events:
        event_name = event.get("name", "")
        event_date = event.get("date", "")
        term = event.get("term", "")
        
        term_str = f"({term} Dönemi)" if term else ""
        full_content += f"**{event_name}** {term_str}: {event_date}\n\n"
    
    # Yaz Dönemi
    summer_term = data.get("summer_term", {})
    if summer_term:
        full_content += f"## {summer_term.get('title', 'Yaz Öğretimi')}\n\n"
        full_content += f"**Tarih Aralığı:** {summer_term.get('date_range', '')}\n\n"
        
        for event in summer_term.get("events", []):
            full_content += f"**{event.get('name', '')}:** {event.get('date', '')}\n\n"
    
    # Resmi Tatiller
    holidays = data.get("official_holidays", {})
    if holidays:
        full_content += f"## {holidays.get('title', 'Resmi Tatiller')}\n\n"
        
        for holiday in holidays.get("holidays", []):
            holiday_name = holiday.get("name", "")
            holiday_date = holiday.get("date", "")
            if holiday_date:
                full_content += f"**{holiday_name}:** {holiday_date}\n\n"
            else:
                full_content += f"**{holiday_name}**\n\n"
    
    # Notlar
    notes = data.get("notes", [])
    if notes:
        full_content += "## Önemli Notlar\n\n"
        for i, note in enumerate(notes, 1):
            full_content += f"{i}. {note}\n\n"
    
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
    guz_events = [event for event in events if "Güz" in event.get("name", "") or event.get("term") == "Güz"]
    if guz_events:
        guz_content = f"# {university_name} - Güz Dönemi Akademik Takvim ({academic_year})\n\n"
        
        for event in guz_events:
            event_name = event.get("name", "")
            event_date = event.get("date", "")
            guz_content += f"**{event_name}:** {event_date}\n\n"
        
        # İlgili tatilleri ekle (Eylül-Ocak arası)
        guz_content += "## Güz Dönemindeki Resmi Tatiller\n\n"
        for holiday in holidays.get("holidays", []):
            holiday_name = holiday.get("name", "")
            holiday_date = holiday.get("date", "")
            # Güz dönemine denk düşen tatilleri filtrele (Eylül-Ocak arası)
            if holiday_date and ("Ekim" in holiday_date or "Kasım" in holiday_date or "Aralık" in holiday_date or 
                               ("Ocak" in holiday_date and "2026" in holiday_date)):
                guz_content += f"**{holiday_name}:** {holiday_date}\n\n"
        
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
    bahar_events = [event for event in events if "Bahar" in event.get("name", "") or event.get("term") == "Bahar"]
    if bahar_events:
        bahar_content = f"# {university_name} - Bahar Dönemi Akademik Takvim ({academic_year})\n\n"
        
        for event in bahar_events:
            event_name = event.get("name", "")
            event_date = event.get("date", "")
            bahar_content += f"**{event_name}:** {event_date}\n\n"
        
        # İlgili tatilleri ekle (Şubat-Haziran arası)
        bahar_content += "## Bahar Dönemindeki Resmi Tatiller\n\n"
        for holiday in holidays.get("holidays", []):
            holiday_name = holiday.get("name", "")
            holiday_date = holiday.get("date", "")
            # Bahar dönemine denk düşen tatilleri filtrele (Şubat-Haziran arası)
            if holiday_date and ("Şubat" in holiday_date or "Mart" in holiday_date or "Nisan" in holiday_date or 
                              "Mayıs" in holiday_date or ("Haziran" in holiday_date and "2026" in holiday_date)):
                bahar_content += f"**{holiday_name}:** {holiday_date}\n\n"
        
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
    
    # Yaz Dönemi ayrı dokümanı
    if summer_term:
        yaz_content = f"# {university_name} - Yaz Dönemi Akademik Takvim ({academic_year})\n\n"
        yaz_content += f"## {summer_term.get('title', 'Yaz Öğretimi')}\n"
        yaz_content += f"**Tarih Aralığı:** {summer_term.get('date_range', '')}\n\n"
        
        for event in summer_term.get("events", []):
            yaz_content += f"**{event.get('name', '')}:** {event.get('date', '')}\n\n"
        
        # İlgili tatilleri ekle (Haziran-Eylül arası)
        yaz_content += "## Yaz Dönemindeki Resmi Tatiller\n\n"
        for holiday in holidays.get("holidays", []):
            holiday_name = holiday.get("name", "")
            holiday_date = holiday.get("date", "")
            # Yaz dönemine denk düşen tatilleri filtrele (Haziran-Eylül arası)
            if holiday_date and ("Haziran" in holiday_date or "Temmuz" in holiday_date or "Ağustos" in holiday_date or 
                              ("Eylül" in holiday_date and "2026" in holiday_date)):
                yaz_content += f"**{holiday_name}:** {holiday_date}\n\n"
        
        yaz_hash = compute_hash(yaz_content)
        documents.append(Document(
            page_content=yaz_content,
            metadata={
                "hash": yaz_hash,
                "title": f"{university_name} - Yaz Dönemi Akademik Takvim",
                "university": university_name,
                "academic_year": academic_year,
                "donem": "yaz",
                "document_type": "akademik_takvim_donem",
                "source": source_file,
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Sınavlar dokümanı
    sinav_content = f"# {university_name} - Sınavlar Takvimi ({academic_year})\n\n"
    
    # Güz dönemi sınavları
    sinav_content += "## Güz Dönemi Sınavları\n\n"
    for event in events:
        if ("Güz" in event.get("name", "") or event.get("term") == "Güz") and ("Sınav" in event.get("name", "") or "sınav" in event.get("name", "").lower()):
            sinav_content += f"**{event.get('name', '')}:** {event.get('date', '')}\n\n"
    
    # Bahar dönemi sınavları
    sinav_content += "## Bahar Dönemi Sınavları\n\n"
    for event in events:
        if ("Bahar" in event.get("name", "") or event.get("term") == "Bahar") and ("Sınav" in event.get("name", "") or "sınav" in event.get("name", "").lower()):
            sinav_content += f"**{event.get('name', '')}:** {event.get('date', '')}\n\n"
    
    # Yaz dönemi sınavları
    if summer_term:
        sinav_content += "## Yaz Dönemi Sınavları\n\n"
        for event in summer_term.get("events", []):
            if "Sınav" in event.get("name", "") or "sınav" in event.get("name", "").lower():
                sinav_content += f"**{event.get('name', '')}:** {event.get('date', '')}\n\n"
    
    # Sınav notları
    sinav_content += "## Sınavlarla İlgili Önemli Notlar\n\n"
    for note in notes:
        if "sınav" in note.lower():
            sinav_content += f"- {note}\n\n"
    
    # Yeterince içerik varsa sınav dokümanını ekle
    if len(sinav_content) > 250:  # Başlıkların uzunluğunu aşan bir içerik mevcut mu?
        sinav_hash = compute_hash(sinav_content)
        documents.append(Document(
            page_content=sinav_content,
            metadata={
                "hash": sinav_hash,
                "title": f"{university_name} - Sınavlar Takvimi",
                "university": university_name,
                "academic_year": academic_year,
                "document_type": "sinav_takvim",
                "source": source_file,
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Kayıt işlemleri dokümanı
    kayit_content = f"# {university_name} - Kayıt İşlemleri Takvimi ({academic_year})\n\n"
    
    # Kayıt işlemleri
    for event in events:
        if any(term in event.get("name", "").lower() for term in ["kayıt", "kabul", "yazılma", "kayıtlanma", "ekle-sil", "ödeme"]):
            kayit_content += f"**{event.get('name', '')}:** {event.get('date', '')}\n\n"
    
    # Yaz dönemi kayıt işlemleri
    if summer_term:
        kayit_content += "## Yaz Dönemi Kayıt İşlemleri\n\n"
        for event in summer_term.get("events", []):
            if any(term in event.get("name", "").lower() for term in ["kayıt", "kabul"]):
                kayit_content += f"**{event.get('name', '')}:** {event.get('date', '')}\n\n"
    
    # Kayıt işlemleri notları
    kayit_content += "## Kayıt İşlemleri ile İlgili Önemli Notlar\n\n"
    for note in notes:
        if any(term in note.lower() for term in ["kayıt", "yazılma", "derse yazılma", "ödeme", "ücret"]):
            kayit_content += f"- {note}\n\n"
    
    # Yeterince içerik varsa kayıt işlemleri dokümanını ekle
    if len(kayit_content) > 250:
        kayit_hash = compute_hash(kayit_content)
        documents.append(Document(
            page_content=kayit_content,
            metadata={
                "hash": kayit_hash,
                "title": f"{university_name} - Kayıt İşlemleri Takvimi",
                "university": university_name,
                "academic_year": academic_year,
                "document_type": "kayit_takvim",
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