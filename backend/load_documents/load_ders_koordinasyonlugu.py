import json
from langchain.schema import Document
import hashlib
import os
from typing import List, Dict, Any
import glob


def compute_hash(content: str) -> str:
    """
    Computes a SHA256 hash from content to prevent duplicate document loading.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Ders koordinasyonu JSON dosyasını işleyerek LangChain Document nesnelerine dönüştürür.
    
    Args:
        data: Yüklenen JSON verisi.
        source_file: Kaynak dosya adı.
        
    Returns:
        Document nesnelerinden oluşan bir liste.
    """
    documents = []
    
    # Döküman başlık bilgisi
    doc_title = data.get("document_name", "")
    doc_date = data.get("document_date", "")
    doc_number = data.get("document_number", "")
    
    # Ana doküman bilgisi
    main_content = f"{doc_title}\n"
    if doc_date:
        main_content += f"Tarih: {doc_date}\n"
    if doc_number:
        main_content += f"Sayı: {doc_number}\n"
    
    main_content += f"\n{data.get('approval_info', '')}\n\n"
    
    # Tüm bölümleri dolaş
    for section in data.get("sections", []):
        section_name = section.get("section_name", "")
        section_title = section.get("section_title", "")
        
        section_content = f"{section_name}: {section_title}\n\n"
        
        # Her bölümün maddelerini dolaş
        for article in section.get("articles", []):
            article_number = article.get("article_number", "")
            article_title = article.get("article_title", "")
            
            article_content = f"MADDE {article_number} – {article_title}\n"
            
            # Paragraflar varsa ekle
            for i, paragraph in enumerate(article.get("paragraphs", [])):
                article_content += f"({i+1}) {paragraph}\n\n"
            
            # Fıkralar varsa ekle
            if "clauses" in article:
                for clause in article.get("clauses", []):
                    article_content += f"{clause.get('clause_letter', '')}) {clause.get('content', '')}\n"
            
            section_content += article_content + "\n"
        
        # Her bölüm için bir dokuman oluştur
        doc_hash = compute_hash(section_content)
        documents.append(Document(
            page_content=section_content,
            metadata={
                "hash": doc_hash,
                "title": doc_title,
                "section": section_name,
                "source": source_file
            }
        ))
        
        # Ana içeriğe de ekle
        main_content += section_content + "\n"
    
    # Ana doküman için bir dokuman oluştur
    doc_hash = compute_hash(main_content)
    documents.append(Document(
        page_content=main_content,
        metadata={
            "hash": doc_hash,
            "title": doc_title,
            "section": "full_document",
            "source": source_file
        }
    ))
    
    # Ekleri işle
    for attachment in data.get("attachments", []):
        attachment_number = attachment.get("attachment_number", "")
        attachment_title = attachment.get("attachment_title", "")
        
        attachment_content = f"EK {attachment_number}: {attachment_title}\n\n"
        
        # Derslerin tablosunu oluştur
        attachment_content += "Kod | Ders Adı | T | U | L | Kredi | AKTS\n"
        attachment_content += "-----|---------|---|---|---|-------|------\n"
        
        for course in attachment.get("courses", []):
            course_row = f"{course.get('code', '')} | {course.get('name', '')} | {course.get('T', '')} | "
            course_row += f"{course.get('U', '')} | {course.get('L', '')} | {course.get('credit', '')} | {course.get('ects', '')}\n"
            attachment_content += course_row
        
        # Her ek için bir dokuman oluştur
        doc_hash = compute_hash(attachment_content)
        documents.append(Document(
            page_content=attachment_content,
            metadata={
                "hash": doc_hash,
                "title": doc_title,
                "section": f"attachment_{attachment_number}",
                "attachment_title": attachment_title,
                "source": source_file
            }
        ))
    
    return documents