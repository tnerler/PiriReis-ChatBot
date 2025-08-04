from langchain.schema import Document
import hashlib
from typing import List, Dict, Any


def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Lisansüstü Eğitim Enstitüsü Akademik Takvim JSON verisini işleyerek Document nesneleri oluşturur.
    """
    documents = []
    current_date = "2025-07-31 08:01:24"
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
    
    # Akademik Takvim - Yarıyıllar
    terms = data.get("academic_calendar", {}).get("terms", [])
    
    for term in terms:
        term_name = term.get("name", "")
        full_content += f"## {term_name}\n\n"
        
        # Genel etkinlikler
        events = term.get("events", [])
        for event in events:
            event_name = event.get("name", "")
            event_date = event.get("date", "")
            full_content += f"**{event_name}:** {event_date}\n\n"
        
        # Doktora programı etkinlikleri
        doctoral_program = term.get("doctoral_program", {})
        if doctoral_program:
            full_content += f"### {doctoral_program.get('name', 'Doktora Programı')}\n\n"
            
            for event in doctoral_program.get("events", []):
                event_name = event.get("name", "")
                event_date = event.get("date", "")
                note = event.get("note", "")
                details = event.get("details", "")
                
                full_content += f"**{event_name}**"
                if event_date:
                    full_content += f": {event_date}"
                full_content += "\n\n"
                
                if note:
                    full_content += f"*Not: {note}*\n\n"
                if details:
                    full_content += f"*Detay: {details}*\n\n"
        
        # Yüksek lisans programı etkinlikleri
        masters_program = term.get("masters_program", {})
        if masters_program:
            full_content += f"### {masters_program.get('name', 'Yüksek Lisans Programı')}\n\n"
            
            for event in masters_program.get("events", []):
                event_name = event.get("name", "")
                event_date = event.get("date", "")
                note = event.get("note", "")
                
                full_content += f"**{event_name}**"
                if event_date:
                    full_content += f": {event_date}"
                full_content += "\n\n"
                
                if note:
                    full_content += f"*Not: {note}*\n\n"
    
    # Resmi Tatiller
    holidays = data.get("official_holidays", {})
    if holidays:
        full_content += f"## {holidays.get('title', 'Resmi Tatiller')}\n\n"
        
        for holiday in holidays.get("holidays", []):
            holiday_name = holiday.get("name", "")
            holiday_date = holiday.get("date", "")
            
            full_content += f"**{holiday_name}**"
            if holiday_date:
                full_content += f": {holiday_date}"
            full_content += "\n\n"
    
    # Notlar
    notes = data.get("notes", [])
    if notes:
        full_content += "## Önemli Notlar\n\n"
        for note in notes:
            full_content += f"- {note}\n\n"
    
    # Ana takvim dokümanını ekle
    main_hash = compute_hash(full_content)
    documents.append(Document(
        page_content=full_content,
        metadata={
            "hash": main_hash,
            "title": f"{university_name} - {doc_title}",
            "university": university_name,
            "academic_year": academic_year,
            "document_type": "lisansustu_akademik_takvim",
            "source": source_file,
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    # Güz Dönemi dokümanı
    if len(terms) > 0:
        guz_term = terms[0]  # İlk dönem (Güz)
        guz_content = f"# {university_name} - Lisansüstü Eğitim Enstitüsü Güz Dönemi Akademik Takvim ({academic_year})\n\n"
        
        # Genel etkinlikler
        for event in guz_term.get("events", []):
            event_name = event.get("name", "")
            event_date = event.get("date", "")
            guz_content += f"**{event_name}:** {event_date}\n\n"
        
        # Doktora programı
        doctoral_program = guz_term.get("doctoral_program", {})
        if doctoral_program:
            guz_content += f"## {doctoral_program.get('name', 'Doktora Programı')}\n\n"
            
            for event in doctoral_program.get("events", []):
                event_name = event.get("name", "")
                event_date = event.get("date", "")
                note = event.get("note", "")
                
                guz_content += f"**{event_name}**"
                if event_date:
                    guz_content += f": {event_date}"
                guz_content += "\n\n"
                
                if note:
                    guz_content += f"*Not: {note}*\n\n"
        
        # Yüksek lisans programı
        masters_program = guz_term.get("masters_program", {})
        if masters_program:
            guz_content += f"## {masters_program.get('name', 'Yüksek Lisans Programı')}\n\n"
            
            for event in masters_program.get("events", []):
                event_name = event.get("name", "")
                event_date = event.get("date", "")
                note = event.get("note", "")
                
                guz_content += f"**{event_name}**"
                if event_date:
                    guz_content += f": {event_date}"
                guz_content += "\n\n"
                
                if note:
                    guz_content += f"*Not: {note}*\n\n"
        
        # Güz dönemindeki tatiller
        guz_content += "## Güz Dönemindeki Resmi Tatiller\n\n"
        for holiday in holidays.get("holidays", []):
            holiday_date = holiday.get("date", "")
            if holiday_date and any(ay in holiday_date for ay in ["Eylül", "Ekim", "Kasım", "Aralık", "Ocak"]) and "2025" in holiday_date:
                holiday_name = holiday.get("name", "")
                guz_content += f"**{holiday_name}:** {holiday_date}\n\n"
        
        guz_hash = compute_hash(guz_content)
        documents.append(Document(
            page_content=guz_content,
            metadata={
                "hash": guz_hash,
                "title": f"{university_name} - Lisansüstü Eğitim Enstitüsü Güz Dönemi Akademik Takvim",
                "university": university_name,
                "academic_year": academic_year,
                "donem": "guz",
                "document_type": "lisansustu_donem_takvim",
                "source": source_file,
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Bahar Dönemi dokümanı
    if len(terms) > 1:
        bahar_term = terms[1]  # İkinci dönem (Bahar)
        bahar_content = f"# {university_name} - Lisansüstü Eğitim Enstitüsü Bahar Dönemi Akademik Takvim ({academic_year})\n\n"
        
        # Genel etkinlikler
        for event in bahar_term.get("events", []):
            event_name = event.get("name", "")
            event_date = event.get("date", "")
            bahar_content += f"**{event_name}:** {event_date}\n\n"
        
        # Doktora programı
        doctoral_program = bahar_term.get("doctoral_program", {})
        if doctoral_program:
            bahar_content += f"## {doctoral_program.get('name', 'Doktora Programı')}\n\n"
            
            for event in doctoral_program.get("events", []):
                event_name = event.get("name", "")
                event_date = event.get("date", "")
                note = event.get("note", "")
                
                bahar_content += f"**{event_name}**"
                if event_date:
                    bahar_content += f": {event_date}"
                bahar_content += "\n\n"
                
                if note:
                    bahar_content += f"*Not: {note}*\n\n"
        
        # Yüksek lisans programı
        masters_program = bahar_term.get("masters_program", {})
        if masters_program:
            bahar_content += f"## {masters_program.get('name', 'Yüksek Lisans Programı')}\n\n"
            
            for event in masters_program.get("events", []):
                event_name = event.get("name", "")
                event_date = event.get("date", "")
                note = event.get("note", "")
                
                bahar_content += f"**{event_name}**"
                if event_date:
                    bahar_content += f": {event_date}"
                bahar_content += "\n\n"
                
                if note:
                    bahar_content += f"*Not: {note}*\n\n"
        
        # Bahar dönemindeki tatiller
        bahar_content += "## Bahar Dönemindeki Resmi Tatiller\n\n"
        for holiday in holidays.get("holidays", []):
            holiday_date = holiday.get("date", "")
            if holiday_date and any(ay in holiday_date for ay in ["Şubat", "Mart", "Nisan", "Mayıs", "Haziran"]) and "2026" in holiday_date:
                holiday_name = holiday.get("name", "")
                bahar_content += f"**{holiday_name}:** {holiday_date}\n\n"
        
        bahar_hash = compute_hash(bahar_content)
        documents.append(Document(
            page_content=bahar_content,
            metadata={
                "hash": bahar_hash,
                "title": f"{university_name} - Lisansüstü Eğitim Enstitüsü Bahar Dönemi Akademik Takvim",
                "university": university_name,
                "academic_year": academic_year,
                "donem": "bahar",
                "document_type": "lisansustu_donem_takvim",
                "source": source_file,
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Doktora Programı dokümanı
    doktora_content = f"# {university_name} - Lisansüstü Eğitim Enstitüsü Doktora Programı Takvimi ({academic_year})\n\n"
    
    for term_index, term in enumerate(terms):
        term_name = term.get("name", "")
        doctoral_program = term.get("doctoral_program", {})
        
        if doctoral_program and doctoral_program.get("events", []):
            doktora_content += f"## {term_name} - {doctoral_program.get('name', 'Doktora Programı')}\n\n"
            
            for event in doctoral_program.get("events", []):
                event_name = event.get("name", "")
                event_date = event.get("date", "")
                note = event.get("note", "")
                details = event.get("details", "")
                
                doktora_content += f"**{event_name}**"
                if event_date:
                    doktora_content += f": {event_date}"
                doktora_content += "\n\n"
                
                if note:
                    doktora_content += f"*Not: {note}*\n\n"
                if details:
                    doktora_content += f"*Detay: {details}*\n\n"
    
    # Yeterince doktora içeriği varsa doktora dokümanını ekle
    if len(doktora_content) > 300:  # Başlık dışında içerik var mı?
        doktora_hash = compute_hash(doktora_content)
        documents.append(Document(
            page_content=doktora_content,
            metadata={
                "hash": doktora_hash,
                "title": f"{university_name} - Lisansüstü Eğitim Enstitüsü Doktora Programı Takvimi",
                "university": university_name,
                "academic_year": academic_year,
                "program": "doktora",
                "document_type": "lisansustu_program_takvim",
                "source": source_file,
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Yüksek Lisans Programı dokümanı
    yuksek_lisans_content = f"# {university_name} - Lisansüstü Eğitim Enstitüsü Yüksek Lisans Programı Takvimi ({academic_year})\n\n"
    
    for term_index, term in enumerate(terms):
        term_name = term.get("name", "")
        masters_program = term.get("masters_program", {})
        
        if masters_program and masters_program.get("events", []):
            yuksek_lisans_content += f"## {term_name} - {masters_program.get('name', 'Yüksek Lisans Programı')}\n\n"
            
            for event in masters_program.get("events", []):
                event_name = event.get("name", "")
                event_date = event.get("date", "")
                note = event.get("note", "")
                
                yuksek_lisans_content += f"**{event_name}**"
                if event_date:
                    yuksek_lisans_content += f": {event_date}"
                yuksek_lisans_content += "\n\n"
                
                if note:
                    yuksek_lisans_content += f"*Not: {note}*\n\n"
    
    # Yeterince yüksek lisans içeriği varsa yüksek lisans dokümanını ekle
    if len(yuksek_lisans_content) > 300:  # Başlık dışında içerik var mı?
        yuksek_lisans_hash = compute_hash(yuksek_lisans_content)
        documents.append(Document(
            page_content=yuksek_lisans_content,
            metadata={
                "hash": yuksek_lisans_hash,
                "title": f"{university_name} - Lisansüstü Eğitim Enstitüsü Yüksek Lisans Programı Takvimi",
                "university": university_name,
                "academic_year": academic_year,
                "program": "yuksek_lisans",
                "document_type": "lisansustu_program_takvim",
                "source": source_file,
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Sınav Takvimi dokümanı
    sinav_content = f"# {university_name} - Lisansüstü Eğitim Enstitüsü Sınav Takvimi ({academic_year})\n\n"
    
    # Güz dönemi sınavları
    if len(terms) > 0:
        sinav_content += "## Güz Dönemi Sınavları\n\n"
        
        # Genel sınavlar
        for event in terms[0].get("events", []):
            if "sınav" in event.get("name", "").lower():
                event_name = event.get("name", "")
                event_date = event.get("date", "")
                sinav_content += f"**{event_name}:** {event_date}\n\n"
        
        # Doktora sınavları
        doctoral_program = terms[0].get("doctoral_program", {})
        if doctoral_program:
            sinav_content += "### Doktora Programı Sınavları\n\n"
            for event in doctoral_program.get("events", []):
                if "sınav" in event.get("name", "").lower():
                    event_name = event.get("name", "")
                    event_date = event.get("date", "")
                    note = event.get("note", "")
                    
                    sinav_content += f"**{event_name}:** {event_date}\n"
                    if note:
                        sinav_content += f"*Not: {note}*\n\n"
                    else:
                        sinav_content += "\n"
        
        # Yüksek lisans sınavları
        masters_program = terms[0].get("masters_program", {})
        if masters_program:
            sinav_content += "### Yüksek Lisans Programı Sınavları\n\n"
            for event in masters_program.get("events", []):
                if "sınav" in event.get("name", "").lower():
                    event_name = event.get("name", "")
                    event_date = event.get("date", "")
                    note = event.get("note", "")
                    
                    sinav_content += f"**{event_name}:** {event_date}\n"
                    if note:
                        sinav_content += f"*Not: {note}*\n\n"
                    else:
                        sinav_content += "\n"
    
    # Bahar dönemi sınavları
    if len(terms) > 1:
        sinav_content += "## Bahar Dönemi Sınavları\n\n"
        
        # Genel sınavlar
        for event in terms[1].get("events", []):
            if "sınav" in event.get("name", "").lower():
                event_name = event.get("name", "")
                event_date = event.get("date", "")
                sinav_content += f"**{event_name}:** {event_date}\n\n"
        
        # Doktora sınavları
        doctoral_program = terms[1].get("doctoral_program", {})
        if doctoral_program:
            sinav_content += "### Doktora Programı Sınavları\n\n"
            for event in doctoral_program.get("events", []):
                if "sınav" in event.get("name", "").lower():
                    event_name = event.get("name", "")
                    event_date = event.get("date", "")
                    note = event.get("note", "")
                    
                    sinav_content += f"**{event_name}:** {event_date}\n"
                    if note:
                        sinav_content += f"*Not: {note}*\n\n"
                    else:
                        sinav_content += "\n"
        
        # Yüksek lisans sınavları
        masters_program = terms[1].get("masters_program", {})
        if masters_program:
            sinav_content += "### Yüksek Lisans Programı Sınavları\n\n"
            for event in masters_program.get("events", []):
                if "sınav" in event.get("name", "").lower():
                    event_name = event.get("name", "")
                    event_date = event.get("date", "")
                    note = event.get("note", "")
                    
                    sinav_content += f"**{event_name}:** {event_date}\n"
                    if note:
                        sinav_content += f"*Not: {note}*\n\n"
                    else:
                        sinav_content += "\n"
    
    # Yeterince sınav içeriği varsa sınav dokümanını ekle
    if len(sinav_content) > 300:  # Başlık dışında içerik var mı?
        sinav_hash = compute_hash(sinav_content)
        documents.append(Document(
            page_content=sinav_content,
            metadata={
                "hash": sinav_hash,
                "title": f"{university_name} - Lisansüstü Eğitim Enstitüsü Sınav Takvimi",
                "university": university_name,
                "academic_year": academic_year,
                "document_type": "lisansustu_sinav_takvim",
                "source": source_file,
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Başvuru ve Kayıt İşlemleri dokümanı
    basvuru_content = f"# {university_name} - Lisansüstü Eğitim Enstitüsü Başvuru ve Kayıt Takvimi ({academic_year})\n\n"
    
    # Dönemlere göre başvuru ve kayıt işlemleri
    for term_index, term in enumerate(terms):
        term_name = term.get("name", "")
        basvuru_content += f"## {term_name} Başvuru ve Kayıt İşlemleri\n\n"
        
        for event in term.get("events", []):
            event_name = event.get("name", "").lower()
            if any(keyword in event_name for keyword in ["başvuru", "kayıt", "mülakat", "ilan", "kesin kayıt"]):
                event_name_orig = event.get("name", "")
                event_date = event.get("date", "")
                basvuru_content += f"**{event_name_orig}:** {event_date}\n\n"
    
    # Yeterince başvuru ve kayıt içeriği varsa dokümanı ekle
    if len(basvuru_content) > 300:  # Başlık dışında içerik var mı?
        basvuru_hash = compute_hash(basvuru_content)
        documents.append(Document(
            page_content=basvuru_content,
            metadata={
                "hash": basvuru_hash,
                "title": f"{university_name} - Lisansüstü Eğitim Enstitüsü Başvuru ve Kayıt Takvimi",
                "university": university_name,
                "academic_year": academic_year,
                "document_type": "lisansustu_basvuru_takvim",
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