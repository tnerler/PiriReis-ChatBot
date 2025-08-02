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
    Erasmus için anlaşmalı üniversiteleri listesini işleyerek 
    LangChain Document nesnelerine dönüştürür.
    
    Args:
        data: Yüklenen JSON verisi.
        source_file: Kaynak dosya adı.
        
    Returns:
        Document nesnelerinden oluşan bir liste.
    """
    documents = []
    current_date = "2025-07-25 07:32:06"  # UTC format
    user_login = "tnerler"
    
    # Ana bilgileri al
    doc_title = data.get("document_title", "")
    metadata = data.get("metadata", {})
    
    # Tüm üniversiteleri içeren ana metin oluştur
    full_content = f"{doc_title}\n\n"
    full_content += f"Son Güncelleme: {metadata.get('last_updated', '')}\n"
    full_content += f"Toplam Anlaşmalı Üniversite Sayısı: {metadata.get('total_universities', 0)}\n"
    full_content += f"Anlaşmalı Ülke Sayısı: {metadata.get('total_countries', 0)}\n\n"
    
    # Her fakülte için bir doküman oluştur
    for department in data.get("departments", []):
        department_name = department.get("department_name", "")
        universities = department.get("universities", [])
        
        # Fakülte içeriği oluştur
        department_content = f"{department_name} Erasmus Anlaşmalı Üniversiteler\n\n"
        department_content += "Üniversite Adı | Ülke\n"
        department_content += "-------------|------\n"
        
        # Üniversiteleri ekle
        for university in universities:
            uni_name = university.get("name", "")
            country = university.get("country", "")
            department_content += f"{uni_name} | {country}\n"
        
        # Ana metne fakülte içeriğini ekle
        full_content += f"# {department_name}\n\n"
        full_content += department_content + "\n\n"
        
        # Fakülte bazlı doküman oluştur
        dept_hash = compute_hash(department_content)
        documents.append(Document(
            page_content=department_content,
            metadata={
                "hash": dept_hash,
                "title": f"{department_name} Erasmus Anlaşmalı Üniversiteler",
                "department": department_name,
                "university_count": len(universities),
                "source": source_file,
                "document_type": "erasmus_department",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
        
        # Ülke bazlı gruplandırma yap
        country_map = {}
        for university in universities:
            country = university.get("country", "")
            uni_name = university.get("name", "")
            
            if country not in country_map:
                country_map[country] = []
            
            country_map[country].append(uni_name)
        
        # Her ülke için doküman oluştur
        for country, unis in country_map.items():
            country_content = f"{department_name} - {country} Anlaşmalı Üniversiteler\n\n"
            
            for uni in unis:
                country_content += f"- {uni}\n"
            
            country_hash = compute_hash(country_content)
            documents.append(Document(
                page_content=country_content,
                metadata={
                    "hash": country_hash,
                    "title": f"{department_name} - {country} Anlaşmalı Üniversiteler",
                    "department": department_name,
                    "country": country,
                    "university_count": len(unis),
                    "source": source_file,
                    "document_type": "erasmus_country",
                    "processed_date": current_date,
                    "processed_by": user_login
                }
            ))
    
    # Ülke bazlı ana doküman oluştur
    all_countries = {}
    for department in data.get("departments", []):
        department_name = department.get("department_name", "")
        universities = department.get("universities", [])
        
        for university in universities:
            country = university.get("country", "")
            uni_name = university.get("name", "")
            dept = department_name
            
            if country not in all_countries:
                all_countries[country] = []
            
            all_countries[country].append({
                "university": uni_name,
                "department": dept
            })
    
    # Her ülke için genel doküman oluştur
    for country, unis in all_countries.items():
        country_content = f"{country} - Erasmus Anlaşmalı Üniversiteler\n\n"
        
        for uni in unis:
            country_content += f"- {uni['university']} ({uni['department']})\n"
        
        country_hash = compute_hash(country_content)
        documents.append(Document(
            page_content=country_content,
            metadata={
                "hash": country_hash,
                "title": f"{country} - Erasmus Anlaşmalı Üniversiteler",
                "country": country,
                "university_count": len(unis),
                "source": source_file,
                "document_type": "erasmus_by_country",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Arama dostu bir doküman oluştur - tüm üniversitelerin düz listesi
    search_content = "Erasmus Anlaşmalı Üniversiteler Listesi\n\n"
    all_universities = []
    
    for department in data.get("departments", []):
        department_name = department.get("department_name", "")
        universities = department.get("universities", [])
        
        for university in universities:
            uni_name = university.get("name", "")
            country = university.get("country", "")
            
            all_universities.append({
                "name": uni_name,
                "country": country,
                "department": department_name
            })
    
    # Üniversite adına göre sırala
    all_universities.sort(key=lambda x: x["name"])
    
    for uni in all_universities:
        search_content += f"{uni['name']} - {uni['country']} ({uni['department']})\n"
    
    search_hash = compute_hash(search_content)
    documents.append(Document(
        page_content=search_content,
        metadata={
            "hash": search_hash,
            "title": "Erasmus Anlaşmalı Üniversiteler - Alfabetik Liste",
            "university_count": len(all_universities),
            "source": source_file,
            "document_type": "erasmus_search_list",
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    # Tam doküman
    full_hash = compute_hash(full_content)
    documents.append(Document(
        page_content=full_content,
        metadata={
            "hash": full_hash,
            "title": doc_title,
            "university_count": metadata.get("total_universities", 0),
            "country_count": metadata.get("total_countries", 0),
            "source": source_file,
            "document_type": "erasmus_full",
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    return documents