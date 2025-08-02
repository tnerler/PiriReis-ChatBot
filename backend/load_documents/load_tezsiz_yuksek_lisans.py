from langchain.schema import Document
import hashlib
from typing import List
from datetime import datetime

def compute_hash(content: str) -> str:
    """İçeriğin benzersiz hash değerini hesaplar."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Yüksek lisans programları JSON verisini işleyerek Document nesneleri oluşturur.
    
    Parameters:
    -----------
    data : dict
        İşlenecek JSON verisi
    source_file : str
        Kaynak dosya yolu
        
    Returns:
    --------
    List[Document]
        Oluşturulan Document nesneleri listesi
    """
    documents = []
    current_date = "2025-07-29 10:52:05"
    user_login = "tnerler"
    
    # Temel bilgileri al
    title = data.get("title", "Lisansüstü Programlar")
    programs = data.get("programs", [])
    metadata = data.get("metadata", {})
    
    # Ana doküman içeriği oluştur
    full_content = f"# {title}\n\n"
    
    # Her program için
    for program in programs:
        program_name = program.get("name", "")
        language = program.get("language", "")
        description = program.get("description", "")
        
        # Ana dokümana özet ekle
        full_content += f"## {program_name}\n\n"
        
        if language:
            full_content += f"**Eğitim Dili:** {language}\n\n"
            
        if description:
            full_content += f"{description}\n\n"
            
        # Program için ayrıntılı içerik oluştur
        program_content = f"# {program_name}\n\n"
        
        if language:
            program_content += f"**Eğitim Dili:** {language}\n\n"
            
        if description:
            program_content += f"## Program Tanımı\n\n{description}\n\n"
        
        # Program detayları
        if "program_details" in program:
            details = program.get("program_details", "")
            program_content += f"## Program Detayları\n\n{details}\n\n"
            
        # Program özellikleri
        if "features" in program:
            features = program.get("features", "")
            program_content += f"## Program Özellikleri\n\n{features}\n\n"
            
        # Kariyer olanakları
        if "career_opportunities" in program:
            career = program.get("career_opportunities", "")
            program_content += f"## Kariyer Olanakları\n\n{career}\n\n"
            
        # Program hedefleri
        if "program_goals" in program:
            goals = program.get("program_goals", [])
            program_content += f"## Program Hedefleri\n\n"
            
            if isinstance(goals, list):
                for goal in goals:
                    program_content += f"- {goal}\n"
            else:
                program_content += f"{goals}\n"
                
            program_content += "\n"
            
        # Kabul edilen mezuniyet alanları
        if "eligible_backgrounds" in program:
            backgrounds = program.get("eligible_backgrounds", [])
            program_content += f"## Kabul Edilen Mezuniyet Alanları\n\n"
            
            for bg in backgrounds:
                program_content += f"- {bg}\n"
                
            program_content += "\n"
            
        # Müfredat linki
        if "curriculum_url" in program:
            url = program.get("curriculum_url", "")
            program_content += f"## Müfredat\n\n[Ders programı için tıklayınız]({url})\n\n"
            
        # Program için özel gereksinimler
        if "special_requirements" in program:
            req = program.get("special_requirements", "")
            program_content += f"## Özel Gereksinimler\n\n{req}\n\n"
            
        # Her program için bir doküman oluştur
        program_hash = compute_hash(program_content)
        documents.append(Document(
            page_content=program_content,
            metadata={
                "hash": program_hash,
                "title": program_name,
                "language": language,
                "program_type": title,
                "source": source_file,
                "document_type": "program_detay",
                "curriculum_url": program.get("curriculum_url", ""),
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
        
    # Programlar için özet tablosu oluştur
    full_content += "\n## Programlar Özet Tablosu\n\n"
    full_content += "| Program Adı | Eğitim Dili | Mezuniyet Alanları Sayısı | Müfredat Linki |\n"
    full_content += "|-------------|------------|--------------------------|---------------|\n"
    
    for program in programs:
        program_name = program.get("name", "")
        language = program.get("language", "-")
        bg_count = len(program.get("eligible_backgrounds", []))
        curriculum_url = program.get("curriculum_url", "-")
        
        if curriculum_url != "-":
            curriculum_cell = f"[Müfredat]({curriculum_url})"
        else:
            curriculum_cell = "-"
            
        full_content += f"| {program_name} | {language} | {bg_count} | {curriculum_cell} |\n"
    
    # Program türlerine göre dokümanlar oluştur
    program_languages = {}
    
    # Dillere göre programları grupla
    for program in programs:
        lang = program.get("language", "Belirtilmemiş")
        if lang not in program_languages:
            program_languages[lang] = []
        program_languages[lang].append(program)
    
    # Her dil için özet doküman oluştur
    for lang, lang_programs in program_languages.items():
        lang_content = f"# {lang} {title}\n\n"
        
        for program in lang_programs:
            program_name = program.get("name", "")
            description = program.get("description", "")
            
            lang_content += f"## {program_name}\n\n"
            lang_content += f"{description}\n\n"
            
            # Müfredat linki
            if "curriculum_url" in program:
                url = program.get("curriculum_url", "")
                lang_content += f"[Ders programı için tıklayınız]({url})\n\n"
        
        # Dile göre doküman oluştur
        lang_hash = compute_hash(lang_content)
        documents.append(Document(
            page_content=lang_content,
            metadata={
                "hash": lang_hash,
                "title": f"{lang} {title}",
                "language": lang,
                "program_type": title,
                "source": source_file,
                "document_type": "program_dil",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Ana doküman ekle
    full_hash = compute_hash(full_content)
    documents.append(Document(
        page_content=full_content,
        metadata={
            "hash": full_hash,
            "title": title,
            "program_count": len(programs),
            "source": source_file,
            "document_type": "program_tam",
            "file_name": metadata.get("file_name", source_file.split("/")[-1] if "/" in source_file else source_file),
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    return documents