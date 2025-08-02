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
    Piri Reis Üniversitesi Üniforma Yönetmeliği JSON verisini işleyerek 
    LangChain Document nesnelerine dönüştürür.
    
    Args:
        data: Yüklenen JSON verisi.
        source_file: Kaynak dosya adı.
        
    Returns:
        Document nesnelerinden oluşan bir liste.
    """
    documents = []
    
    # Belge üst bilgileri
    doc_title = data.get("document_name", "")
    doc_header = data.get("document_header", "")
    approval_info = data.get("approval_info", "")
    
    # Belgenin tamamını içeren ana metin oluşturma
    full_content = f"{doc_header}\n{doc_title}\n{approval_info}\n\n"
    
    # Her bölüm için bir doküman oluştur
    for section in data.get("sections", []):
        section_name = section.get("section_name", "")
        section_title = section.get("section_title", "")
        
        # Bölüm içeriği oluşturma
        section_content = f"{section_name}\n{section_title}\n\n"
        
        # Her maddeyi işle
        for article in section.get("articles", []):
            article_number = article.get("article_number", "")
            article_title = article.get("article_title", "")
            
            # Madde başlığı
            if article_title:
                section_content += f"Madde {article_number} - {article_title}\n\n"
            else:
                section_content += f"Madde {article_number}\n\n"
            
            # Paragrafları ekle
            for paragraph in article.get("paragraphs", []):
                section_content += f"{paragraph}\n\n"
            
            # Tanımları ekle
            if "definitions" in article:
                for definition in article.get("definitions", []):
                    term = definition.get("term", "")
                    definition_text = definition.get("definition", "")
                    
                    section_content += f"{term}: {definition_text}\n"
                section_content += "\n"
            
            # Alt fıkraları ekle
            if "sub_clauses" in article:
                for clause in article.get("sub_clauses", []):
                    clause_letter = clause.get("clause_letter", "")
                    content = clause.get("content", "")
                    
                    section_content += f"{clause_letter}) {content}\n\n"
        
        # Bölüm bazlı doküman oluştur
        section_hash = compute_hash(section_content)
        documents.append(Document(
            page_content=section_content,
            metadata={
                "hash": section_hash,
                "title": doc_title,
                "section": section_name,
                "section_title": section_title,
                "source": source_file,
                "document_type": "yonetmelik_bolum",
                "processed_date": "2025-07-25 07:21:41",
                "processed_by": "tnerler"
            }
        ))
        
        # Ana içeriğe bölüm içeriğini ekle
        full_content += section_content + "\n"
        
        # Her madde için ayrı doküman oluştur
        for article in section.get("articles", []):
            article_number = article.get("article_number", "")
            article_title = article.get("article_title", "")
            
            # Madde içeriği
            article_content = ""
            if article_title:
                article_content += f"Madde {article_number} - {article_title}\n\n"
            else:
                article_content += f"Madde {article_number}\n\n"
            
            # Paragrafları ekle
            for paragraph in article.get("paragraphs", []):
                article_content += f"{paragraph}\n\n"
            
            # Tanımları ekle
            if "definitions" in article:
                for definition in article.get("definitions", []):
                    term = definition.get("term", "")
                    definition_text = definition.get("definition", "")
                    
                    article_content += f"{term}: {definition_text}\n"
                article_content += "\n"
            
            # Alt fıkraları ekle
            if "sub_clauses" in article:
                for clause in article.get("sub_clauses", []):
                    clause_letter = clause.get("clause_letter", "")
                    content = clause.get("content", "")
                    
                    article_content += f"{clause_letter}) {content}\n\n"
            
            # Madde bazlı doküman oluştur
            article_hash = compute_hash(article_content)
            documents.append(Document(
                page_content=article_content,
                metadata={
                    "hash": article_hash,
                    "title": doc_title,
                    "section": section_name,
                    "section_title": section_title,
                    "article_number": article_number,
                    "article_title": article_title,
                    "source": source_file,
                    "document_type": "yonetmelik_madde",
                    "processed_date": "2025-07-25 07:21:41",
                    "processed_by": "tnerler"
                }
            ))
    
    # Ekleri işleyerek ek dokümanları oluştur
    attachments_content = ""
    for attachment in data.get("attachments", []):
        attachment_name = attachment.get("attachment_name", "")
        attachments_content += f"{attachment_name}\n\n"
        
        # Şekilleri ekle
        for figure in attachment.get("figures", []):
            figure_id = figure.get("figure_id", "")
            figure_title = figure.get("figure_title", "")
            reference = figure.get("reference", "")
            
            if reference:
                attachments_content += f"{figure_id} - {figure_title} ({reference})\n"
            else:
                attachments_content += f"{figure_id} - {figure_title}\n"
        attachments_content += "\n"
        
        # Notları ekle
        for note in attachment.get("notes", []):
            attachments_content += f"{note}\n"
        attachments_content += "\n"
    
    if attachments_content:
        # Ekler bazlı doküman oluştur
        attachments_hash = compute_hash(attachments_content)
        documents.append(Document(
            page_content=attachments_content,
            metadata={
                "hash": attachments_hash,
                "title": doc_title,
                "section": "Ekler",
                "source": source_file,
                "document_type": "yonetmelik_ekler",
                "processed_date": "2025-07-25 07:21:41",
                "processed_by": "tnerler"
            }
        ))
        
        # Ana içeriğe ekleri ekle
        full_content += "EKLER\n\n" + attachments_content
    
    # Tam döküman için bir Document oluştur
    full_hash = compute_hash(full_content)
    documents.append(Document(
        page_content=full_content,
        metadata={
            "hash": full_hash,
            "title": doc_title,
            "source": source_file,
            "document_type": "yonetmelik_tam",
            "processed_date": "2025-07-25 07:21:41",
            "processed_by": "tnerler"
        }
    ))
    
    # Özel amaçlı dokümanlar oluştur
    
    # 1. Üniforma kuralları dokümanı
    uniform_rules_content = "ÜNİFORMA TAŞINMA KURALLARI\n\n"
    for section in data.get("sections", []):
        if section.get("section_name") == "DÖRDÜNCÜ BÖLÜM":
            for article in section.get("articles", []):
                article_title = article.get("article_title", "")
                uniform_rules_content += f"{article_title}\n\n"
                
                if "sub_clauses" in article:
                    for clause in article.get("sub_clauses", []):
                        clause_letter = clause.get("clause_letter", "")
                        content = clause.get("content", "")
                        
                        uniform_rules_content += f"{clause_letter}) {content}\n\n"
    
    uniform_rules_hash = compute_hash(uniform_rules_content)
    documents.append(Document(
        page_content=uniform_rules_content,
        metadata={
            "hash": uniform_rules_hash,
            "title": "Üniforma Taşınma Kuralları",
            "source": source_file,
            "document_type": "yonetmelik_kurallar",
            "processed_date": "2025-07-25 07:21:41",
            "processed_by": "tnerler"
        }
    ))
    
    # 2. Üniforma alametleri dokümanı
    uniform_emblems_content = "ÜNİFORMA ALAMETLERİ\n\n"
    for section in data.get("sections", []):
        if section.get("section_name") == "ÜÇÜNCÜ BÖLÜM":
            for article in section.get("articles", []):
                if article.get("article_title") == "Üniformanın Alametleri":
                    for paragraph in article.get("paragraphs", []):
                        uniform_emblems_content += f"{paragraph}\n\n"
                    
                    if "sub_clauses" in article:
                        for clause in article.get("sub_clauses", []):
                            clause_letter = clause.get("clause_letter", "")
                            content = clause.get("content", "")
                            
                            uniform_emblems_content += f"{clause_letter}) {content}\n\n"
    
    uniform_emblems_hash = compute_hash(uniform_emblems_content)
    documents.append(Document(
        page_content=uniform_emblems_content,
        metadata={
            "hash": uniform_emblems_hash,
            "title": "Üniforma Alametleri",
            "source": source_file,
            "document_type": "yonetmelik_alametler",
            "processed_date": "2025-07-25 07:21:41",
            "processed_by": "tnerler"
        }
    ))
    
    # 3. Kıyafet dönemleri dokümanı
    uniform_periods_content = "KIYAFET DÖNEMLERİ\n\n"
    for section in data.get("sections", []):
        if section.get("section_name") == "İKİNCİ BÖLÜM":
            for article in section.get("articles", []):
                if "definitions" in article:
                    for definition in article.get("definitions", []):
                        if definition.get("term") in ["Kışlık Kıyafet Dönemi", "Yazlık Kıyafet Dönemi"]:
                            term = definition.get("term", "")
                            definition_text = definition.get("definition", "")
                            
                            uniform_periods_content += f"{term}: {definition_text}\n\n"
    
    uniform_periods_hash = compute_hash(uniform_periods_content)
    documents.append(Document(
        page_content=uniform_periods_content,
        metadata={
            "hash": uniform_periods_hash,
            "title": "Üniforma Kıyafet Dönemleri",
            "source": source_file,
            "document_type": "yonetmelik_donemler",
            "processed_date": "2025-07-25 07:21:41",
            "processed_by": "tnerler"
        }
    ))
    
    return documents