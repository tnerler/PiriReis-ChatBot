import json
from langchain.schema import Document
import hashlib
import os
from typing import List, Dict, Any
import re

def compute_hash(content: str) -> str:
    """
    Computes a SHA256 hash from content to prevent duplicate document loading.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def extract_section_with_header(content: str, header_pattern=r'^#{1,6}\s+(.+)$', min_length=50):
    """
    Parses the markdown content and extracts sections with headers.
    Returns a list of (header, content) tuples.
    """
    lines = content.split('\n')
    sections = []
    current_header = None
    current_content = []
    
    for line in lines:
        header_match = re.match(header_pattern, line)
        
        if header_match:
            # If we have a previous section, save it
            if current_header and current_content:
                section_content = '\n'.join(current_content).strip()
                if len(section_content) >= min_length:
                    sections.append((current_header, section_content))
            
            # Start a new section
            current_header = header_match.group(1).strip()
            current_content = []
        else:
            # Add line to current section
            if current_header is not None:
                current_content.append(line)
    
    # Don't forget the last section
    if current_header and current_content:
        section_content = '\n'.join(current_content).strip()
        if len(section_content) >= min_length:
            sections.append((current_header, section_content))
    
    return sections

def extract_tables(content: str):
    """
    Extracts tables from markdown content.
    Returns a list of table contents.
    """
    # Simple markdown table extraction (basic version)
    table_pattern = r'\|(.+)\|\s*\n\|(?:\s*[-:]+\s*\|)+\s*\n((?:\|.+\|\s*\n)+)'
    tables = []
    
    for match in re.finditer(table_pattern, content, re.MULTILINE):
        header = match.group(1).strip()
        rows = match.group(2).strip()
        table_content = f"|{header}|\n{rows}"
        tables.append(table_content)
    
    return tables

def process_data(data: str, source_file: str) -> List[Document]:
    """
    İşlev, PRU broşürünün MD dosyasını işleyerek LangChain Document nesnelerine dönüştürür.
    
    Args:
        data: Markdown içeriği.
        source_file: Kaynak dosya adı.
        
    Returns:
        Document nesnelerinden oluşan bir liste.
    """
    documents = []
    
    # Üniversite adını çıkar
    university_name = "Piri Reis Üniversitesi"
    
    # 1. Tüm içeriği tek bir dokuman olarak ekle
    full_content_hash = compute_hash(data)
    documents.append(Document(
        page_content=data,
        metadata={
            "hash": full_content_hash,
            "university": university_name,
            "document_type": "full_brochure",
            "source": source_file
        }
    ))
    
    # 2. Başlık bölümlerine göre dokümanlar oluştur
    sections = extract_section_with_header(data)
    
    for header, section_content in sections:
        # Anahtar kelimelerle bölüm tipini belirle
        section_type = "general"
        if any(keyword in header.lower() for keyword in ["fakülte", "faculty"]):
            section_type = "faculty"
        elif any(keyword in header.lower() for keyword in ["program", "bölüm", "department"]):
            section_type = "program"
        elif any(keyword in header.lower() for keyword in ["iş olanakları", "job", "career"]):
            section_type = "career_opportunities"
        elif "kampüs" in header.lower() or "campus" in header.lower():
            section_type = "campus"
        elif any(keyword in header.lower() for keyword in ["simülat", "simulat", "laboratuvar", "lab"]):
            section_type = "facilities"
        elif any(keyword in header.lower() for keyword in ["aktivite", "etkinlik", "kulüp", "club", "activity"]):
            section_type = "student_activities"
        
        # Her bölüm için bir dokuman oluştur
        section_hash = compute_hash(header + section_content)
        documents.append(Document(
            page_content=section_content,
            metadata={
                "hash": section_hash,
                "university": university_name,
                "section": header,
                "section_type": section_type,
                "source": source_file
            }
        ))
    
    # 3. Tabloları çıkar
    tables = extract_tables(data)
    
    for i, table_content in enumerate(tables):
        table_hash = compute_hash(table_content)
        documents.append(Document(
            page_content=table_content,
            metadata={
                "hash": table_hash,
                "university": university_name,
                "section_type": "table",
                "table_index": i,
                "source": source_file
            }
        ))
    
    # 4. Fakülte ve Bölüm Bilgilerini Çıkar
    # Fakülte başlıklarını ve içeriklerini bul
    faculty_headers = re.finditer(r'#{1,3}\s+(.*FAKÜLTESİ|.*MESLEK YÜKSEKOKULU)', data)
    
    faculty_sections = {}
    last_faculty = None
    
    # Fakülte bölümlerini belirleme
    for match in faculty_headers:
        faculty_name = match.group(1).strip()
        faculty_sections[faculty_name] = []
        last_faculty = faculty_name
    
    # Program/Bölüm bilgilerini çıkar
    program_sections = re.finditer(r'#{1,3}\s+([^#]+?)(?=\n#{1,3}|\Z)', data)
    
    for match in program_sections:
        program_content = match.group(1).strip()
        first_line = program_content.split('\n')[0]
        
        # Eğer bu bir bölüm veya program başlığı ise
        if not first_line.endswith("FAKÜLTESİ") and not first_line.endswith("MESLEK YÜKSEKOKULU") and "Başkan" not in first_line:
            program_name = first_line
            program_details = program_content[len(program_name):].strip()
            
            if program_details and last_faculty:
                # İş olanakları bölümünü bul
                job_opportunities = ""
                job_match = re.search(r'#{1,3}\s+İş Olanakları\s*([\s\S]*?)(?=#{1,3}|$)', program_details)
                
                if job_match:
                    job_opportunities = job_match.group(1).strip()
                
                # Her program/bölüm için doküman oluştur
                program_hash = compute_hash(program_name + program_details)
                documents.append(Document(
                    page_content=program_details,
                    metadata={
                        "hash": program_hash,
                        "university": university_name,
                        "faculty": last_faculty,
                        "program": program_name,
                        "job_opportunities": bool(job_opportunities),
                        "document_type": "program_details",
                        "source": source_file
                    }
                ))
                
                # İş olanakları ayrı bir dokuman olarak
                if job_opportunities:
                    job_hash = compute_hash(job_opportunities)
                    documents.append(Document(
                        page_content=job_opportunities,
                        metadata={
                            "hash": job_hash,
                            "university": university_name,
                            "faculty": last_faculty,
                            "program": program_name,
                            "document_type": "job_opportunities",
                            "source": source_file
                        }
                    ))
    
    # 5. Piri Reis tarihi bilgisini çıkar
    history_match = re.search(r'TÜRK DENİZCİLİK TARİHİNİN PARLAYAN YILDIZI([\s\S]*?)(?=#{1,3}|---)', data)
    if history_match:
        history_content = history_match.group(1).strip()
        history_hash = compute_hash(history_content)
        documents.append(Document(
            page_content=history_content,
            metadata={
                "hash": history_hash,
                "university": university_name,
                "section_type": "history",
                "document_type": "piri_reis_history",
                "source": source_file
            }
        ))
    
    # 6. İletişim bilgilerini çıkar
    contact_pattern = r'Tuzla Deniz Kampüsü[\s\S]*?(?=\Z)'
    contact_match = re.search(contact_pattern, data)
    if contact_match:
        contact_info = contact_match.group(0).strip()
        contact_hash = compute_hash(contact_info)
        documents.append(Document(
            page_content=contact_info,
            metadata={
                "hash": contact_hash,
                "university": university_name,
                "section_type": "contact",
                "document_type": "contact_information",
                "source": source_file
            }
        ))
    
    return documents