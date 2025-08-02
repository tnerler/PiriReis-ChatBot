from langchain.schema import Document
import hashlib
from typing import List, Dict, Any


def compute_hash(content: str) -> str:
    """
    Computes a SHA256 hash from content to prevent duplicate document loading.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()
def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Piri Reis Üniversitesi Ön Lisans ve Lisans Eğitim-Öğretim ve Sınav Yönetmeliği JSON 
    verisini işleyerek LangChain Document nesnelerine dönüştürür.
    
    Args:
        data: Yüklenen JSON verisi.
        source_file: Kaynak dosya adı.
        
    Returns:
        Document nesnelerinden oluşan bir liste.
    """
    documents = []
    
    # Döküman başlığı ve genel bilgiler
    doc_title = data.get("document_name", "")
    doc_date = data.get("document_date", "")
    doc_number = data.get("document_number", "")
    
    # Yönetmeliğin tamamını içeren ana metin oluşturma
    full_content = f"{doc_title}\n\n"
    full_content += f"Tarih: {doc_date}\n"
    full_content += f"Sayı: {doc_number}\n\n"
    
    # Yayın bilgileri varsa ekle
    if "publication_info" in data:
        pub_info = data.get("publication_info", {})
        full_content += f"Yayın: {pub_info.get('source', '')} - {pub_info.get('day', '')}\n\n"
    
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
            section_content += f"MADDE {article_number} - {article_title}\n\n"
            
            # Paragrafları ekle
            if "paragraphs" in article:
                for paragraph in article.get("paragraphs", []):
                    section_content += f"{paragraph}\n\n"
            
            # Tanımları ekle
            if "definitions" in article:
                for definition in article.get("definitions", []):
                    term_letter = definition.get("term_letter", "")
                    term = definition.get("term", "")
                    definition_text = definition.get("definition", "")
                    
                    section_content += f"{term_letter}) {term}: {definition_text}\n"
                section_content += "\n"
            
            # Alt fıkraları ekle
            if "sub_clauses" in article:
                for clause in article.get("sub_clauses", []):
                    clause_letter = clause.get("clause_letter", "")
                    content = clause.get("content", "")
                    
                    section_content += f"{clause_letter}) {content}\n"
                section_content += "\n"
            
            # Ek paragrafları ekle
            if "additional_paragraphs" in article:
                for add_paragraph in article.get("additional_paragraphs", []):
                    section_content += f"{add_paragraph}\n\n"
            
            # Not tablosunu ekle
            if "grade_table" in article:
                section_content += "Başarı Harfi | Başarı Katsayısı | Puan | Açıklama\n"
                section_content += "-------------|-----------------|------|----------\n"
                
                for grade in article.get("grade_table", []):
                    success_letter = grade.get("success_letter", "")
                    success_coefficient = grade.get("success_coefficient", "")
                    points = grade.get("points", "")
                    description = grade.get("description", "")
                    
                    section_content += f"{success_letter} | {success_coefficient} | {points} | {description}\n"
                section_content += "\n"
            
            # Özel notları ekle
            if "special_grades" in article:
                section_content += "Harf | Anlamı\n"
                section_content += "-----|-------\n"
                
                for grade in article.get("special_grades", []):
                    letter = grade.get("letter", "")
                    meaning = grade.get("meaning", "")
                    
                    section_content += f"{letter} | {meaning}\n"
                section_content += "\n"
            
            # Özel not açıklamalarını ekle
            if "special_grades_descriptions" in article:
                for desc in article.get("special_grades_descriptions", []):
                    letter = desc.get("letter", "")
                    description = desc.get("description", "")
                    
                    section_content += f"{letter}) {description}\n\n"
        
        # Bölüm bazlı doküman oluştur
        section_hash = compute_hash(section_content)
        documents.append(Document(
            page_content=section_content,
            metadata={
                "hash": section_hash,
                "title": doc_title,
                "section": section_name,
                "section_title": section_title,
                "document_date": doc_date,
                "document_number": doc_number,
                "source": source_file,
                "document_type": "yonetmelik_bolum"
            }
        ))
        
        # Ana içeriğe bölüm içeriğini ekle
        full_content += section_content + "\n"
        
        # Her madde için ayrı doküman oluştur
        for article in section.get("articles", []):
            article_number = article.get("article_number", "")
            article_title = article.get("article_title", "")
            
            # Madde içeriği
            article_content = f"MADDE {article_number} - {article_title}\n\n"
            
            # Paragrafları ekle
            if "paragraphs" in article:
                for paragraph in article.get("paragraphs", []):
                    article_content += f"{paragraph}\n\n"
            
            # Tanımları ekle
            if "definitions" in article:
                for definition in article.get("definitions", []):
                    term_letter = definition.get("term_letter", "")
                    term = definition.get("term", "")
                    definition_text = definition.get("definition", "")
                    
                    article_content += f"{term_letter}) {term}: {definition_text}\n"
                article_content += "\n"
            
            # Alt fıkraları ekle
            if "sub_clauses" in article:
                for clause in article.get("sub_clauses", []):
                    clause_letter = clause.get("clause_letter", "")
                    content = clause.get("content", "")
                    
                    article_content += f"{clause_letter}) {content}\n"
                article_content += "\n"
            
            # Ek paragrafları ekle
            if "additional_paragraphs" in article:
                for add_paragraph in article.get("additional_paragraphs", []):
                    article_content += f"{add_paragraph}\n\n"
            
            # Not tablosunu ekle
            if "grade_table" in article:
                article_content += "Başarı Harfi | Başarı Katsayısı | Puan | Açıklama\n"
                article_content += "-------------|-----------------|------|----------\n"
                
                for grade in article.get("grade_table", []):
                    success_letter = grade.get("success_letter", "")
                    success_coefficient = grade.get("success_coefficient", "")
                    points = grade.get("points", "")
                    description = grade.get("description", "")
                    
                    article_content += f"{success_letter} | {success_coefficient} | {points} | {description}\n"
                article_content += "\n"
            
            # Özel notları ekle
            if "special_grades" in article:
                article_content += "Harf | Anlamı\n"
                article_content += "-----|-------\n"
                
                for grade in article.get("special_grades", []):
                    letter = grade.get("letter", "")
                    meaning = grade.get("meaning", "")
                    
                    article_content += f"{letter} | {meaning}\n"
                article_content += "\n"
            
            # Özel not açıklamalarını ekle
            if "special_grades_descriptions" in article:
                for desc in article.get("special_grades_descriptions", []):
                    letter = desc.get("letter", "")
                    description = desc.get("description", "")
                    
                    article_content += f"{letter}) {description}\n\n"
            
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
                    "document_date": doc_date,
                    "document_number": doc_number,
                    "source": source_file,
                    "document_type": "yonetmelik_madde"
                }
            ))
    
    # Tam döküman için bir Document oluştur
    full_hash = compute_hash(full_content)
    documents.append(Document(
        page_content=full_content,
        metadata={
            "hash": full_hash,
            "title": doc_title,
            "document_date": doc_date,
            "document_number": doc_number,
            "source": source_file,
            "document_type": "yonetmelik_tam"
        }
    ))
    
    # Belirli maddeleri gruplandırarak doküman oluştur
    # Örneğin: Değerlendirme ve notlandırma ile ilgili maddeler
    grading_articles = []
    for section in data.get("sections", []):
        section_name = section.get("section_name", "")
        if section_name == "DÖRDÜNCÜ BÖLÜM":  # Sınavlar, Notlar ve Başarı Değerlendirmesi bölümü
            for article in section.get("articles", []):
                article_number = article.get("article_number", "")
                article_title = article.get("article_title", "")
                
                # Madde içeriği
                article_content = f"MADDE {article_number} - {article_title}\n\n"
                
                # Paragrafları ekle
                if "paragraphs" in article:
                    for paragraph in article.get("paragraphs", []):
                        article_content += f"{paragraph}\n\n"
                
                # Not tablosunu ekle
                if "grade_table" in article:
                    article_content += "Başarı Harfi | Başarı Katsayısı | Puan | Açıklama\n"
                    article_content += "-------------|-----------------|------|----------\n"
                    
                    for grade in article.get("grade_table", []):
                        success_letter = grade.get("success_letter", "")
                        success_coefficient = grade.get("success_coefficient", "")
                        points = grade.get("points", "")
                        description = grade.get("description", "")
                        
                        article_content += f"{success_letter} | {success_coefficient} | {points} | {description}\n"
                    article_content += "\n"
                
                # Özel notları ekle
                if "special_grades" in article:
                    article_content += "Harf | Anlamı\n"
                    article_content += "-----|-------\n"
                    
                    for grade in article.get("special_grades", []):
                        letter = grade.get("letter", "")
                        meaning = grade.get("meaning", "")
                        
                        article_content += f"{letter} | {meaning}\n"
                    article_content += "\n"
                
                # Özel not açıklamalarını ekle
                if "special_grades_descriptions" in article:
                    for desc in article.get("special_grades_descriptions", []):
                        letter = desc.get("letter", "")
                        description = desc.get("description", "")
                        
                        article_content += f"{letter}) {description}\n\n"
                
                grading_articles.append(article_content)
    
    # Notlandırma maddelerini içeren bir doküman oluştur
    if grading_articles:
        grading_content = f"{doc_title} - NOTLANDIRMA VE DEĞERLENDİRME\n\n"
        for content in grading_articles:
            grading_content += content + "\n"
        
        grading_hash = compute_hash(grading_content)
        documents.append(Document(
            page_content=grading_content,
            metadata={
                "hash": grading_hash,
                "title": doc_title,
                "document_date": doc_date,
                "document_number": doc_number,
                "source": source_file,
                "document_type": "yonetmelik_notlandirma"
            }
        ))
    
    # Metadata bilgisi
    current_date = "2025-07-25 07:15:07"
    user_login = "tnerler"
    
    # Metadata eklentisi
    for doc in documents:
        doc.metadata["processed_date"] = current_date
        doc.metadata["processed_by"] = user_login
    
    return documents