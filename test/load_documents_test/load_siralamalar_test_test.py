from langchain.schema import Document
import hashlib
from typing import List, Dict, Any
import json
from datetime import datetime


def compute_hash(content: str) -> str:
    """
    Computes a SHA256 hash from content to prevent duplicate document loading.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Piri Reis Üniversitesi bölüm sıralama ve puanları JSON verisini işleyerek 
    LangChain Document nesnelerine dönüştürür.
    
    Args:
        data: Yüklenen JSON verisi.
        source_file: Kaynak dosya adı.
        
    Returns:
        Document nesnelerinden oluşan bir liste.
    """
    documents = []
    current_date = "2025-07-25 07:36:59"  # UTC format
    user_login = "tnerler"
    
    # Ana bilgileri al
    doc_title = data.get("document_title", "")
    academic_year = data.get("academic_year", "")
    university_name = data.get("university_name", "")
    metadata = data.get("metadata", {})
    
    # Tüm fakülteleri kapsayan ana doküman oluştur
    full_content = f"{doc_title}\n\n"
    full_content += f"Akademik Yıl: {academic_year}\n"
    full_content += f"Üniversite: {university_name}\n\n"
    
    # Her fakülte için içerik oluştur
    for faculty in data.get("faculties", []):
        faculty_name = faculty.get("faculty_name", "")
        programs = faculty.get("programs", [])
        
        full_content += f"## {faculty_name}\n\n"
        
        for program in programs:
            program_name = program.get("program_name", "")
            program_type = program.get("program_type", "")
            point_type = program.get("point_type", "")
            
            full_content += f"### {program_name} ({program_type} - {point_type})\n\n"
            
            for scholarship in program.get("scholarships", []):
                s_type = scholarship.get("type", "")
                quota = scholarship.get("quota", "")
                min_score = scholarship.get("min_score", "-")
                max_score = scholarship.get("max_score", "-")
                min_rank = scholarship.get("min_rank", "-")
                max_rank = scholarship.get("max_rank", "-")
                
                full_content += f"**{s_type}**\n"
                full_content += f"- Kontenjan: {quota}\n"
                if min_score != "-":
                    full_content += f"- Taban Puan: {min_score}\n"
                if max_score != "-":
                    full_content += f"- Tavan Puan: {max_score}\n"
                if min_rank != "-":
                    full_content += f"- Taban Başarı Sırası: {min_rank}\n"
                if max_rank != "-":
                    full_content += f"- Tavan Başarı Sırası: {max_rank}\n"
                
                special_quotas = scholarship.get("special_quotas", {})
                if special_quotas:
                    full_content += "- Özel Kontenjanlar:\n"
                    for quota_type, quota_count in special_quotas.items():
                        if quota_type == "sehit_gazi":
                            quota_name = "Şehit/Gazi Yakını"
                        elif quota_type == "depremzede":
                            quota_name = "Depremzede"
                        else:
                            quota_name = quota_type
                        full_content += f"  - {quota_name}: {quota_count}\n"
                
                full_content += "\n"
            
            full_content += "\n"
    
    # Tam doküman
    full_hash = compute_hash(full_content)
    documents.append(Document(
        page_content=full_content,
        metadata={
            "hash": full_hash,
            "title": doc_title,
            "university": university_name,
            "academic_year": academic_year,
            "source": source_file,
            "document_type": "siralama_tam",
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    # Her fakülte için bir doküman oluştur
    for faculty in data.get("faculties", []):
        faculty_name = faculty.get("faculty_name", "")
        programs = faculty.get("programs", [])
        
        faculty_content = f"{university_name} - {faculty_name} - {academic_year} Yılı Taban Puanları ve Başarı Sıralamaları\n\n"
        
        for program in programs:
            program_name = program.get("program_name", "")
            program_type = program.get("program_type", "")
            point_type = program.get("point_type", "")
            
            faculty_content += f"## {program_name} ({program_type} - {point_type})\n\n"
            
            # Burs türlerine göre tabloyu oluştur
            faculty_content += "| Burs Türü | Kontenjan | Taban Puan | Tavan Puan | Taban Sıra | Tavan Sıra |\n"
            faculty_content += "|-----------|-----------|------------|------------|------------|------------|\n"
            
            for scholarship in program.get("scholarships", []):
                s_type = scholarship.get("type", "")
                quota = scholarship.get("quota", "-")
                min_score = scholarship.get("min_score", "-")
                max_score = scholarship.get("max_score", "-")
                min_rank = scholarship.get("min_rank", "-")
                max_rank = scholarship.get("max_rank", "-")
                
                faculty_content += f"| {s_type} | {quota} | {min_score} | {max_score} | {min_rank} | {max_rank} |\n"
            
            faculty_content += "\n"
            
            # Özel kontenjanları listele
            has_special_quotas = False
            special_quotas_content = "### Özel Kontenjanlar\n\n"
            
            for scholarship in program.get("scholarships", []):
                special_quotas = scholarship.get("special_quotas", {})
                if special_quotas:
                    has_special_quotas = True
                    s_type = scholarship.get("type", "")
                    special_quotas_content += f"**{s_type}**\n"
                    
                    for quota_type, quota_count in special_quotas.items():
                        if quota_type == "sehit_gazi":
                            quota_name = "Şehit/Gazi Yakını"
                        elif quota_type == "depremzede":
                            quota_name = "Depremzede"
                        else:
                            quota_name = quota_type
                        special_quotas_content += f"- {quota_name}: {quota_count}\n"
                    
                    special_quotas_content += "\n"
            
            if has_special_quotas:
                faculty_content += special_quotas_content
            
            faculty_content += "\n"
        
        faculty_hash = compute_hash(faculty_content)
        documents.append(Document(
            page_content=faculty_content,
            metadata={
                "hash": faculty_hash,
                "title": f"{university_name} - {faculty_name} - {academic_year} Taban Puanları",
                "university": university_name,
                "faculty": faculty_name,
                "academic_year": academic_year,
                "source": source_file,
                "document_type": "siralama_fakulte",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Her program için bir doküman oluştur
    for faculty in data.get("faculties", []):
        faculty_name = faculty.get("faculty_name", "")
        programs = faculty.get("programs", [])
        
        for program in programs:
            program_name = program.get("program_name", "")
            program_type = program.get("program_type", "")
            point_type = program.get("point_type", "")
            
            program_content = f"{university_name} - {program_name} - {academic_year} Yılı Taban Puanları ve Başarı Sıralamaları\n\n"
            program_content += f"Fakülte: {faculty_name}\n"
            program_content += f"Program Türü: {program_type}\n"
            program_content += f"Puan Türü: {point_type}\n\n"
            
            # Burs türlerine göre tabloyu oluştur
            program_content += "| Burs Türü | Kontenjan | Taban Puan | Tavan Puan | Taban Sıralama | Tavan Sıralama |\n"
            program_content += "|-----------|-----------|------------|------------|----------------|----------------|\n"

            for scholarship in program.get("scholarships", []):
                s_type = scholarship.get("type", "")
                quota = scholarship.get("quota", "-")
                min_score = scholarship.get("min_score", "-")
                max_score = scholarship.get("max_score", "-")
                min_rank = scholarship.get("min_rank", "-")
                max_rank = scholarship.get("max_rank", "-")
                
                program_content += f"| {s_type} | {quota} | {min_score} | {max_score} | {min_rank} | {max_rank} |\n"
            
            program_content += "\n"
            
            # Özel kontenjanları listele
            has_special_quotas = False
            special_quotas_content = "## Özel Kontenjanlar\n\n"
            
            for scholarship in program.get("scholarships", []):
                special_quotas = scholarship.get("special_quotas", {})
                if special_quotas:
                    has_special_quotas = True
                    s_type = scholarship.get("type", "")
                    special_quotas_content += f"**{s_type}**\n"
                    
                    for quota_type, quota_count in special_quotas.items():
                        if quota_type == "sehit_gazi":
                            quota_name = "Şehit/Gazi Yakını"
                        elif quota_type == "depremzede":
                            quota_name = "Depremzede"
                        else:
                            quota_name = quota_type
                        special_quotas_content += f"- {quota_name}: {quota_count}\n"
                    
                    special_quotas_content += "\n"
            
            if has_special_quotas:
                program_content += special_quotas_content
            
            # Her burs türü için ayrıntılı bilgi
            program_content += "## Burs Türlerine Göre Ayrıntılı Bilgiler\n\n"
            
            for scholarship in program.get("scholarships", []):
                s_type = scholarship.get("type", "")
                quota = scholarship.get("quota", "-")
                min_score = scholarship.get("min_score", "-")
                max_score = scholarship.get("max_score", "-")
                min_rank = scholarship.get("min_rank", "-")
                max_rank = scholarship.get("max_rank", "-")
                
                program_content += f"### {s_type}\n\n"
                program_content += f"- **Kontenjan:** {quota}\n"
                if min_score != "-":
                    program_content += f"- **Taban Puan:** {min_score}\n"
                if max_score != "-":
                    program_content += f"- **Tavan Puan:** {max_score}\n"
                if min_rank != "-":
                    program_content += f"- **Taban Başarı Sırası:** {min_rank}\n"
                if max_rank != "-":
                    program_content += f"- **Tavan Başarı Sırası:** {max_rank}\n"
                
                special_quotas = scholarship.get("special_quotas", {})
                if special_quotas:
                    program_content += "- **Özel Kontenjanlar:**\n"
                    for quota_type, quota_count in special_quotas.items():
                        if quota_type == "sehit_gazi":
                            quota_name = "Şehit/Gazi Yakını"
                        elif quota_type == "depremzede":
                            quota_name = "Depremzede"
                        else:
                            quota_name = quota_type
                        program_content += f"  - {quota_name}: {quota_count}\n"
                
                program_content += "\n"
            
            program_hash = compute_hash(program_content)
            documents.append(Document(
                page_content=program_content,
                metadata={
                    "hash": program_hash,
                    "title": f"{university_name} - {program_name} - {academic_year} Taban Puanları",
                    "university": university_name,
                    "faculty": faculty_name,
                    "program": program_name,
                    "program_type": program_type,
                    "point_type": point_type,
                    "academic_year": academic_year,
                    "source": source_file,
                    "document_type": "siralama_program",
                    "processed_date": current_date,
                    "processed_by": user_login
                }
            ))
    
    # Burs türlerine göre bir doküman oluştur
    for scholarship_type in ["Tam Burslu", "%50 Burslu", "Ücretli"]:
        scholarship_content = f"{university_name} - {scholarship_type} Bölümler - {academic_year} Taban Puanları ve Başarı Sıralamaları\n\n"
        
        # Taban puana göre sıralama için liste oluştur
        programs_with_scores = []
        
        for faculty in data.get("faculties", []):
            faculty_name = faculty.get("faculty_name", "")
            
            for program in faculty.get("programs", []):
                program_name = program.get("program_name", "")
                program_type = program.get("program_type", "")
                point_type = program.get("point_type", "")
                
                for scholarship in program.get("scholarships", []):
                    if scholarship.get("type") == scholarship_type and "min_score" in scholarship:
                        programs_with_scores.append({
                            "faculty": faculty_name,
                            "program": program_name,
                            "program_type": program_type,
                            "point_type": point_type,
                            "min_score": scholarship.get("min_score", 0),
                            "max_score": scholarship.get("max_score", 0),
                            "min_rank": scholarship.get("min_rank", "-"),
                            "max_rank": scholarship.get("max_rank", "-"),
                            "quota": scholarship.get("quota", "-")
                        })
        
        # Taban puana göre sırala (azalan sırada)
        programs_with_scores.sort(key=lambda x: float(str(x.get("min_score", 0) or 0)), reverse=True)
        
        # Say puan türünü içeren programları listele
        if any(p["point_type"] == "SAY" for p in programs_with_scores):
            scholarship_content += "## SAY Puan Türü\n\n"
            scholarship_content += "| Program | Fakülte | Taban Puan | Tavan Puan | Taban Sıra | Tavan Sıra | Kontenjan |\n"
            scholarship_content += "|---------|---------|------------|------------|------------|------------|----------|\n"
            
            for program in programs_with_scores:
                if program["point_type"] == "SAY":
                    scholarship_content += f"| {program['program']} | {program['faculty']} | {program['min_score']} | {program['max_score']} | {program['min_rank']} | {program['max_rank']} | {program['quota']} |\n"
            
            scholarship_content += "\n"
        
        # EA puan türünü içeren programları listele
        if any(p["point_type"] == "EA" for p in programs_with_scores):
            scholarship_content += "## EA Puan Türü\n\n"
            scholarship_content += "| Program | Fakülte | Taban Puan | Tavan Puan | Taban Sıra | Tavan Sıra | Kontenjan |\n"
            scholarship_content += "|---------|---------|------------|------------|------------|------------|----------|\n"
            
            for program in programs_with_scores:
                if program["point_type"] == "EA":
                    scholarship_content += f"| {program['program']} | {program['faculty']} | {program['min_score']} | {program['max_score']} | {program['min_rank']} | {program['max_rank']} | {program['quota']} |\n"
            
            scholarship_content += "\n"
        
        # TYT puan türünü içeren programları listele
        if any(p["point_type"] == "TYT" for p in programs_with_scores):
            scholarship_content += "## TYT Puan Türü\n\n"
            scholarship_content += "| Program | Fakülte | Taban Puan | Tavan Puan | Taban Sıra | Tavan Sıra | Kontenjan |\n"
            scholarship_content += "|---------|---------|------------|------------|------------|------------|----------|\n"
            
            for program in programs_with_scores:
                if program["point_type"] == "TYT":
                    scholarship_content += f"| {program['program']} | {program['faculty']} | {program['min_score']} | {program['max_score']} | {program['min_rank']} | {program['max_rank']} | {program['quota']} |\n"
        
        scholarship_hash = compute_hash(scholarship_content)
        documents.append(Document(
            page_content=scholarship_content,
            metadata={
                "hash": scholarship_hash,
                "title": f"{university_name} - {scholarship_type} Bölümler - {academic_year} Taban Puanları",
                "university": university_name,
                "scholarship_type": scholarship_type,
                "academic_year": academic_year,
                "source": source_file,
                "document_type": "siralama_burs",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Puan türüne göre bir doküman oluştur
    for point_type in ["SAY", "EA", "TYT"]:
        point_content = f"{university_name} - {point_type} Puan Türü Bölümler - {academic_year} Taban Puanları ve Başarı Sıralamaları\n\n"
        
        # Taban puana göre sıralama için liste oluştur
        programs_with_scores = []
        
        for faculty in data.get("faculties", []):
            faculty_name = faculty.get("faculty_name", "")
            
            for program in faculty.get("programs", []):
                program_name = program.get("program_name", "")
                program_point_type = program.get("point_type", "")
                
                if program_point_type == point_type:
                    for scholarship in program.get("scholarships", []):
                        if "min_score" in scholarship:
                            programs_with_scores.append({
                                "faculty": faculty_name,
                                "program": program_name,
                                "scholarship_type": scholarship.get("type", ""),
                                "min_score": scholarship.get("min_score", 0),
                                "max_score": scholarship.get("max_score", 0),
                                "min_rank": scholarship.get("min_rank", "-"),
                                "max_rank": scholarship.get("max_rank", "-"),
                                "quota": scholarship.get("quota", "-")
                            })
        
        # Taban puana göre sırala (azalan sırada)
        programs_with_scores.sort(key=lambda x: float(str(x.get("min_score", 0) or 0)), reverse=True)
        
        # Tablo şeklinde listele
        point_content += "| Program | Fakülte | Burs Türü | Taban Puan | Tavan Puan | Taban Sıra | Tavan Sıra | Kontenjan |\n"
        point_content += "|---------|---------|-----------|------------|------------|------------|------------|----------|\n"
        
        for program in programs_with_scores:
            point_content += f"| {program['program']} | {program['faculty']} | {program['scholarship_type']} | {program['min_score']} | {program['max_score']} | {program['min_rank']} | {program['max_rank']} | {program['quota']} |\n"
        
        point_hash = compute_hash(point_content)
        documents.append(Document(
            page_content=point_content,
            metadata={
                "hash": point_hash,
                "title": f"{university_name} - {point_type} Puan Türü Bölümler - {academic_year} Taban Puanları",
                "university": university_name,
                "point_type": point_type,
                "academic_year": academic_year,
                "source": source_file,
                "document_type": "siralama_puan_turu",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Soru-cevap formatı için hazırlanmış doküman
    faq_content = f"# {university_name} - {academic_year} Taban Puanları ve Sıralamaları Hakkında Sıkça Sorulan Sorular\n\n"
    
    # Bazı örnek soru-cevaplar oluştur
    faq_content += "## {university_name}'nde en yüksek taban puana sahip bölüm hangisidir?\n\n"
    
    # En yüksek taban puana sahip bölümü bul
    highest_program = {"min_score": 0}
    for faculty in data.get("faculties", []):
        for program in faculty.get("programs", []):
            for scholarship in program.get("scholarships", []):
                if scholarship.get("type") == "Tam Burslu" and "min_score" in scholarship:
                    if float(str(scholarship.get("min_score", 0) or 0)) > float(str(highest_program.get("min_score", 0) or 0)):
                        highest_program = {
                            "program": program.get("program_name", ""),
                            "faculty": faculty.get("faculty_name", ""),
                            "point_type": program.get("point_type", ""),
                            "min_score": scholarship.get("min_score", 0)
                        }
    
    faq_content += f"{university_name}'nde en yüksek taban puana sahip bölüm {highest_program['faculty']} bünyesindeki {highest_program['program']} bölümüdür. Tam burslu kontenjan için taban puan {highest_program['min_score']}'dir ({highest_program['point_type']} puan türünde).\n\n"
    
    faq_content += f"## {university_name}'nde en düşük başarı sırasına sahip bölüm hangisidir?\n\n"
    
    # En düşük başarı sırasına sahip bölümü bul (en iyi sıralama)
    best_rank_program = {"min_rank": float("inf")}
    for faculty in data.get("faculties", []):
        for program in faculty.get("programs", []):
            for scholarship in program.get("scholarships", []):
                if scholarship.get("type") == "Tam Burslu" and "min_rank" in scholarship:
                    rank = int(str(scholarship.get("min_rank", float("inf")) or float("inf")))
                    if rank < best_rank_program.get("min_rank", float("inf")):
                        best_rank_program = {
                            "program": program.get("program_name", ""),
                            "faculty": faculty.get("faculty_name", ""),
                            "point_type": program.get("point_type", ""),
                            "min_rank": rank
                        }
    
    faq_content += f"{university_name}'nde en iyi başarı sırasına sahip bölüm {best_rank_program['faculty']} bünyesindeki {best_rank_program['program']} bölümüdür. Tam burslu kontenjan için taban başarı sırası {best_rank_program['min_rank']}'dir ({best_rank_program['point_type']} puan türünde).\n\n"
    
    faq_content += f"## {university_name} Hukuk Fakültesi'nin taban puanları ve sıralamaları nelerdir?\n\n"
    
    # Hukuk fakültesi için taban puan ve sıralamaları bul
    hukuk_found = False
    for faculty in data.get("faculties", []):
        if "HUKUK" in faculty.get("faculty_name", "").upper():
            hukuk_found = True
            faq_content += f"{university_name} Hukuk Fakültesi {academic_year} yılı için şu taban puan ve sıralama bilgilerine sahiptir:\n\n"
            faq_content += "| Burs Durumu | Taban Puan | Tavan Puan | Taban Sıra | Tavan Sıra | Kontenjan |\n"
            faq_content += "|-------------|------------|------------|------------|------------|----------|\n"
            
            for program in faculty.get("programs", []):
                if program.get("program_name", "").upper() == "HUKUK":
                    for scholarship in program.get("scholarships", []):
                        s_type = scholarship.get("type", "")
                        quota = scholarship.get("quota", "-")
                        min_score = scholarship.get("min_score", "-")
                        max_score = scholarship.get("max_score", "-")
                        min_rank = scholarship.get("min_rank", "-")
                        max_rank = scholarship.get("max_rank", "-")
                        
                        faq_content += f"| {s_type} | {min_score} | {max_score} | {min_rank} | {max_rank} | {quota} |\n"
    
    if not hukuk_found:
        faq_content += f"{university_name} bünyesinde Hukuk Fakültesi bulunmaktadır. Taban puan ve sıralama bilgilerini yukarıdaki tam listeden inceleyebilirsiniz.\n\n"
    
    faq_content += f"## {university_name}'nde hangi burslu programlar bulunmaktadır?\n\n"
    faq_content += f"{university_name}'nde üç farklı burs kategorisinde programlar bulunmaktadır:\n\n"
    faq_content += "1. **Tam Burslu:** Eğitim ücretinin tamamının karşılandığı programlar\n"
    faq_content += "2. **%50 Burslu:** Eğitim ücretinin yarısının karşılandığı programlar\n"
    faq_content += "3. **Ücretli:** Eğitim ücretinin öğrenci tarafından karşılandığı programlar\n\n"
    faq_content += "Her program için bu üç kategoride de kontenjanlar bulunmaktadır. Burs kategorisine göre taban puanlar ve başarı sıralamaları değişmektedir. Tam burslu programlar genellikle daha yüksek taban puan ve daha iyi başarı sıralamasına sahiptir.\n\n"
    
    faq_hash = compute_hash(faq_content)
    documents.append(Document(
        page_content=faq_content,
        metadata={
            "hash": faq_hash,
            "title": f"{university_name} - {academic_year} Taban Puanları Sıkça Sorulan Sorular",
            "university": university_name,
            "academic_year": academic_year,
            "source": source_file,
            "document_type": "siralama_sss",
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    return documents