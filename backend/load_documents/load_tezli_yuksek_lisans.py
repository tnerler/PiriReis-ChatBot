from langchain.schema import Document
import hashlib
from typing import List
from datetime import datetime

def compute_hash(content: str) -> str:
    """İçeriğin benzersiz hash değerini hesaplar."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Tezli Yüksek Lisans programları JSON verisini işleyerek Document nesneleri oluşturur.
    
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
    current_date = "2025-07-29 10:55:27"
    user_login = "tnerler"
    
    # Temel bilgileri al
    title = data.get("title", "Tezli Yüksek Lisans Programları")
    programs = data.get("programs", [])
    metadata = data.get("metadata", {})
    
    # Ana doküman içeriği oluştur
    full_content = f"# {title}\n\n"
    full_content += "Bu belge Piri Reis Üniversitesi'nin tezli yüksek lisans programlarını içermektedir.\n\n"
    
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
            program_content += f"## Program Detayları\n\n"
            
            if isinstance(details, list):
                for detail in details:
                    program_content += f"{detail}\n\n"
            else:
                program_content += f"{details}\n\n"
            
        # Program hedefleri/amaçları
        if "program_goals" in program:
            goals = program.get("program_goals", [])
            program_content += f"## Program Hedefleri\n\n"
            
            if isinstance(goals, list):
                for i, goal in enumerate(goals, 1):
                    program_content += f"{i}. {goal}\n"
            else:
                program_content += f"{goals}\n"
                
            program_content += "\n"
        
        # Program amacı (tekil)
        if "program_goal" in program:
            goal = program.get("program_goal", "")
            program_content += f"## Program Amacı\n\n{goal}\n\n"
            
        # Program yapısı
        if "program_structure" in program:
            structure = program.get("program_structure", "")
            program_content += f"## Program Yapısı\n\n{structure}\n\n"
            
        # Vizyon
        if "vision" in program:
            vision = program.get("vision", "")
            program_content += f"## Vizyon\n\n{vision}\n\n"
            
        # Misyon
        if "mission" in program:
            mission = program.get("mission", "")
            program_content += f"## Misyon\n\n{mission}\n\n"
            
        # Odak alanları
        if "focus_areas" in program:
            focus_areas = program.get("focus_areas", [])
            program_content += f"## Odak Alanları\n\n"
            
            if isinstance(focus_areas, list):
                for area in focus_areas:
                    program_content += f"- {area}\n"
            else:
                program_content += f"{focus_areas}\n"
                
            program_content += "\n"
            
        # Kariyer olanakları
        if "career_opportunities" in program:
            career = program.get("career_opportunities", "")
            program_content += f"## Kariyer Olanakları\n\n{career}\n\n"
            
        # Kabul edilen mezuniyet alanları
        if "eligible_backgrounds" in program:
            backgrounds = program.get("eligible_backgrounds", [])
            program_content += f"## Kabul Edilen Mezuniyet Alanları\n\n"
            
            for bg in backgrounds:
                program_content += f"- {bg}\n"
                
            program_content += "\n"
            
        # Özel gereksinimler
        if "special_requirements" in program:
            req = program.get("special_requirements", "")
            program_content += f"## Özel Gereksinimler\n\n{req}\n\n"
            
        # Müfredat linki
        if "curriculum_url" in program:
            url = program.get("curriculum_url", "")
            program_content += f"## Müfredat\n\n[Ders programı için tıklayınız]({url})\n\n"
            
        # Her program için bir doküman oluştur
        program_hash = compute_hash(program_content)
        documents.append(Document(
            page_content=program_content,
            metadata={
                "hash": program_hash,
                "title": program_name,
                "language": language,
                "program_type": "Tezli Yüksek Lisans",
                "source": source_file,
                "document_type": "program_detay",
                "curriculum_url": program.get("curriculum_url", ""),
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
        
    # Programlar için özet tablosu oluştur
    full_content += "\n## Tezli Yüksek Lisans Programları Özet Tablosu\n\n"
    full_content += "| Program Adı | Eğitim Dili | Alan | Mezuniyet Alanları Sayısı |\n"
    full_content += "|-------------|------------|------|-------------------------|\n"
    
    for program in programs:
        program_name = program.get("name", "")
        language = program.get("language", "-")
        
        # Alan belirle (program adından çıkar)
        program_area = "Genel"
        if "Mühendislik" in program_name:
            if "Makine" in program_name:
                program_area = "Makine Müh."
            elif "Deniz Ulaştırma" in program_name:
                program_area = "Deniz Ulaştırma Müh."
            elif "Elektrik-Elektronik" in program_name:
                program_area = "Elektronik Müh."
            elif "Gemi Makineleri" in program_name:
                program_area = "Gemi Makineleri Müh."
            elif "Hesaplamalı" in program_name:
                program_area = "Hesaplamalı Bilim Müh."
            elif "GİGMM" in program_name:
                program_area = "Deniz Platformları"
            else:
                program_area = "Mühendislik"
        elif "Hukuk" in program_name:
            program_area = "Hukuk"
        elif "İşletme" in program_name:
            program_area = "İşletme"
        elif "Deniz İşletmeciliği" in program_name:
            program_area = "Deniz İşletmeciliği"
            
        bg_count = len(program.get("eligible_backgrounds", []))
        
        full_content += f"| {program_name} | {language} | {program_area} | {bg_count} |\n"
    
    # Dil bazında grupla
    program_languages = {}
    
    # Dillere göre programları grupla
    for program in programs:
        lang = program.get("language", "Belirtilmemiş")
        if lang not in program_languages:
            program_languages[lang] = []
        program_languages[lang].append(program)
    
    # Dil bazlı dokümanlar
    for lang, lang_programs in program_languages.items():
        lang_content = f"# {lang} Tezli Yüksek Lisans Programları\n\n"
        
        for program in lang_programs:
            program_name = program.get("name", "")
            description = program.get("description", "")
            
            lang_content += f"## {program_name}\n\n"
            lang_content += f"{description}\n\n"
            
            # Müfredat linki
            if "curriculum_url" in program:
                url = program.get("curriculum_url", "")
                lang_content += f"[Ders programı için tıklayınız]({url})\n\n"
        
        # Dil bazlı doküman oluştur
        lang_hash = compute_hash(lang_content)
        documents.append(Document(
            page_content=lang_content,
            metadata={
                "hash": lang_hash,
                "title": f"{lang} Tezli Yüksek Lisans Programları",
                "language": lang,
                "program_type": "Tezli Yüksek Lisans",
                "source": source_file,
                "document_type": "program_dil",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Mühendislik programları için ayrı doküman
    engineering_programs = [p for p in programs if "Mühendisliği" in p.get("name", "") or "GİGMM" in p.get("name", "")]
    
    if engineering_programs:
        eng_content = f"# Tezli Yüksek Lisans Mühendislik Programları\n\n"
        eng_content += "Bu belge, Piri Reis Üniversitesi'nin tezli yüksek lisans kapsamındaki mühendislik programlarını içermektedir.\n\n"
        
        for program in engineering_programs:
            program_name = program.get("name", "")
            description = program.get("description", "")
            
            eng_content += f"## {program_name}\n\n"
            eng_content += f"{description}\n\n"
            
            # Program detayları
            if "program_details" in program:
                details = program.get("program_details", "")
                if isinstance(details, list):
                    eng_content += "\n".join(details) + "\n\n"
                else:
                    eng_content += f"{details}\n\n"
            
            # Kabul edilen mezuniyet alanları
            if "eligible_backgrounds" in program:
                eng_content += "**Kabul Edilen Mezuniyet Alanları:** "
                eng_content += ", ".join(program.get("eligible_backgrounds", []))
                eng_content += "\n\n"
        
        # Mühendislik programları dokümanı oluştur
        eng_hash = compute_hash(eng_content)
        documents.append(Document(
            page_content=eng_content,
            metadata={
                "hash": eng_hash,
                "title": "Tezli Yüksek Lisans Mühendislik Programları",
                "field": "Mühendislik",
                "program_type": "Tezli Yüksek Lisans",
                "source": source_file,
                "document_type": "program_alan",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Ana doküman için özet bilgiler
    full_content += "\n## Genel Program Bilgileri\n\n"
    full_content += f"- **Toplam Program Sayısı:** {len(programs)}\n"
    full_content += f"- **Dil Dağılımı:** {', '.join([f'{lang} ({len(prgs)})' for lang, prgs in program_languages.items()])}\n"
    full_content += f"- **Mühendislik Programları:** {len(engineering_programs)}\n"
    full_content += f"- **Diğer Programlar:** {len(programs) - len(engineering_programs)}\n\n"
    
    full_content += "## Başvuru Süreci\n\n"
    full_content += "Tezli yüksek lisans programlarına başvuru için aşağıdaki adımları takip edebilirsiniz:\n\n"
    full_content += "1. Akademik takvimde belirtilen başvuru tarihlerini kontrol edin\n"
    full_content += "2. Başvurmak istediğiniz programın kabul koşullarını inceleyin\n"
    full_content += "3. Online başvuru formunu doldurun\n"
    full_content += "4. Gerekli belgeleri sisteme yükleyin\n"
    full_content += "5. Başvuru ücretini ödeyin\n"
    full_content += "6. Mülakat/yazılı sınav tarihlerini takip edin\n\n"
    
    full_content += "Detaylı bilgi için [Öğrenci İşleri](https://www.pirireis.edu.tr) sayfasını ziyaret edebilirsiniz.\n"
    
    # Ana dokümanı ekle
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