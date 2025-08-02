from langchain.schema import Document
import hashlib
from typing import List
from datetime import datetime

def compute_hash(content: str) -> str:
    """İçeriğin benzersiz hash değerini hesaplar."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Doktora programları JSON verisini işleyerek Document nesneleri oluşturur.
    
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
    current_date = "2025-07-29 10:57:18"
    user_login = "tnerler"
    
    # Temel bilgileri al
    title = data.get("title", "Doktora Programları")
    programs = data.get("programs", [])
    metadata = data.get("metadata", {})
    
    # Ana doküman içeriği oluştur
    full_content = f"# {title}\n\n"
    full_content += "Bu belge Piri Reis Üniversitesi'nin doktora programlarını içermektedir.\n\n"
    
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
                "program_type": "Doktora",
                "source": source_file,
                "document_type": "program_detay",
                "curriculum_url": program.get("curriculum_url", ""),
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
        
    # Programlar için özet tablosu oluştur
    full_content += "\n## Doktora Programları Özet Tablosu\n\n"
    full_content += "| Program Adı | Eğitim Dili | Alan | Mezuniyet Alanları Sayısı |\n"
    full_content += "|-------------|------------|------|-------------------------|\n"
    
    for program in programs:
        program_name = program.get("name", "")
        language = program.get("language", "-")
        
        # Alan belirle (program adından çıkar)
        program_area = "Genel"
        if "Mühendislik" in program_name:
            if "Hesaplamalı Bilim" in program_name:
                program_area = "Hesaplamalı Bilim"
            elif "Deniz Ulaştırma" in program_name:
                program_area = "Deniz Ulaştırma"
            elif "GİGMM" in program_name or "Deniz Platformları" in program_name:
                program_area = "Deniz Platformları"
            else:
                program_area = "Mühendislik"
        elif "Hukuk" in program_name:
            program_area = "Hukuk"
        elif "İşletme" in program_name:
            program_area = "İşletme"
            
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
        lang_content = f"# {lang} Doktora Programları\n\n"
        lang_content += f"Bu belge, Piri Reis Üniversitesi'nin {lang} dilinde eğitim veren doktora programlarını içermektedir.\n\n"
        
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
                "title": f"{lang} Doktora Programları",
                "language": lang,
                "program_type": "Doktora",
                "source": source_file,
                "document_type": "program_dil",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Akademik Kariyer Yolu Dokümanı
    academic_content = f"# Doktora ve Akademik Kariyer Yolu\n\n"
    academic_content += "Bu belge, doktora eğitimi ve akademik kariyer yolu hakkında bilgiler içermektedir.\n\n"
    academic_content += "## Doktora Eğitiminin Önemi\n\n"
    academic_content += "Doktora eğitimi, bir alanda uzmanlaşmanın ve akademik kariyer yolunda ilerlemenin en üst seviyesidir. "
    academic_content += "Doktora derecesi sahipleri, alanlarında özgün araştırmalar yapabilir, yeni bilgiler üretebilir ve "
    academic_content += "bilimsel literatüre katkı sağlayabilir.\n\n"
    
    academic_content += "## Piri Reis Üniversitesi'nde Doktora Programları\n\n"
    
    for program in programs:
        program_name = program.get("name", "")
        academic_content += f"### {program_name}\n\n"
        
        if "description" in program:
            academic_content += f"{program.get('description')}\n\n"
        
        if "program_goals" in program or "program_goal" in program:
            academic_content += "**Hedefler:** "
            if isinstance(program.get("program_goals", ""), list):
                academic_content += ", ".join(program.get("program_goals", []))
            else:
                academic_content += program.get("program_goals", program.get("program_goal", ""))
            academic_content += "\n\n"
    
    academic_content += "## Akademik Kariyer Yolu\n\n"
    academic_content += "1. **Araştırma Görevlisi:** Doktora öğrencileri genellikle bu pozisyondan başlar\n"
    academic_content += "2. **Dr. Öğretim Üyesi:** Doktora derecesi aldıktan sonra ulaşılabilen ilk akademik kadro\n"
    academic_content += "3. **Doçent:** Dr. Öğretim Üyesi olarak belirli süre çalıştıktan ve yeterli yayın ürettikten sonra\n"
    academic_content += "4. **Profesör:** Doçent unvanı ile belirli süre çalıştıktan sonra ulaşılabilen en üst akademik kadro\n\n"
    
    academic_content += "## Doktora Sonrası Fırsatlar\n\n"
    academic_content += "- **Akademik Kariyer:** Üniversitelerde öğretim üyesi olarak görev alma\n"
    academic_content += "- **Araştırma Merkezleri:** Özel veya kamu araştırma merkezlerinde çalışma\n"
    academic_content += "- **Sektör Liderliği:** Özel sektörde üst düzey pozisyonlarda görev alma\n"
    academic_content += "- **Danışmanlık:** Alanında uzman danışman olarak hizmet verme\n"
    
    # Akademik kariyer dokümanı oluştur
    academic_hash = compute_hash(academic_content)
    documents.append(Document(
        page_content=academic_content,
        metadata={
            "hash": academic_hash,
            "title": "Doktora ve Akademik Kariyer Yolu",
            "program_type": "Doktora",
            "source": source_file,
            "document_type": "bilgi_rehberi",
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    # Ana doküman için özet bilgiler
    full_content += "\n## Doktora Programları Hakkında Genel Bilgiler\n\n"
    full_content += f"- **Toplam Program Sayısı:** {len(programs)}\n"
    full_content += f"- **Dil Dağılımı:** {', '.join([f'{lang} ({len(prgs)})' for lang, prgs in program_languages.items()])}\n"
    
    # Doktora alan bazında dağılım
    area_counts = {}
    for program in programs:
        area = "Diğer"
        if "Mühendislik" in program.get("name", ""):
            area = "Mühendislik"
        elif "Hukuk" in program.get("name", ""):
            area = "Hukuk"
        elif "İşletme" in program.get("name", ""):
            area = "İşletme"
            
        if area not in area_counts:
            area_counts[area] = 0
        area_counts[area] += 1
    
    full_content += f"- **Alan Dağılımı:** {', '.join([f'{area} ({count})' for area, count in area_counts.items()])}\n\n"
    
    full_content += "## Doktora Başvuru Süreci\n\n"
    full_content += "Doktora programlarına başvuru için aşağıdaki adımları takip edebilirsiniz:\n\n"
    full_content += "1. Akademik takvimde belirtilen başvuru tarihlerini kontrol edin\n"
    full_content += "2. Başvurmak istediğiniz programın kabul koşullarını ve özel gereksinimlerini inceleyin\n"
    full_content += "3. ALES (en az 55 puan) ve YÖKDİL/YDS (en az 55 puan) sınav sonuçlarınızın geçerlilik sürelerini kontrol edin\n"
    full_content += "4. Online başvuru formunu doldurun ve gerekli belgeleri sisteme yükleyin\n"
    full_content += "5. Bilimsel değerlendirme sınavı ve mülakat aşamalarını takip edin\n"
    full_content += "6. Başvuru sonuçlarını akademik takvimde belirtilen tarihte kontrol edin\n\n"
    
    full_content += "Detaylı bilgi için [Lisansüstü Eğitim Enstitüsü](https://www.pirireis.edu.tr) sayfasını ziyaret edebilirsiniz.\n"
    
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
    
    # Doktora karşılaştırmalı rehber
    comparison_content = "# Doktora ve Yüksek Lisans Programlarının Karşılaştırılması\n\n"
    comparison_content += "Bu belge, doktora ve yüksek lisans programları arasındaki temel farkları açıklamaktadır.\n\n"
    
    comparison_content += "## Temel Farklılıklar\n\n"
    comparison_content += "| Özellik | Yüksek Lisans | Doktora |\n"
    comparison_content += "|---------|--------------|--------|\n"
    comparison_content += "| Süre | Genellikle 2 yıl | Genellikle 4-6 yıl |\n"
    comparison_content += "| Amaç | Uzmanlık kazanma | Özgün bilgi üretme |\n"
    comparison_content += "| Araştırma | Mevcut bilginin sentezi | Yeni bilgi üretimi |\n"
    comparison_content += "| Tez | Daha kısa ve sınırlı | Kapsamlı ve özgün |\n"
    comparison_content += "| Kariyer Hedefi | Uzmanlaşma | Akademik kariyer |\n"
    comparison_content += "| Başvuru Koşulları | Lisans mezunu olmak | Yüksek lisans mezunu olmak |\n"
    
    comparison_content += "\n## Doktora Programlarının Avantajları\n\n"
    comparison_content += "- Alanında en üst düzey uzmanlık\n"
    comparison_content += "- Akademik kariyer fırsatı\n"
    comparison_content += "- Özgün araştırma yapabilme yetkinliği\n"
    comparison_content += "- Sektörde üst düzey pozisyonlara erişim imkanı\n"
    comparison_content += "- Uluslararası araştırma ağlarına dahil olma\n\n"
    
    comparison_content += "## Piri Reis Üniversitesi'nde Doktora Programları\n\n"
    for program in programs:
        comparison_content += f"- **{program.get('name', '')}**: {program.get('language', '')} dilinde eğitim\n"
    
    # Karşılaştırma dokümanı oluştur
    comparison_hash = compute_hash(comparison_content)
    documents.append(Document(
        page_content=comparison_content,
        metadata={
            "hash": comparison_hash,
            "title": "Doktora ve Yüksek Lisans Programlarının Karşılaştırılması",
            "program_type": "Karşılaştırmalı Bilgi",
            "source": source_file,
            "document_type": "karsilastirma",
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    return documents