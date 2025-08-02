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
    İngilizce Hazırlık Yönetmeliği JSON verisini işleyerek 
    LangChain Document nesnelerine dönüştürür.
    
    Args:
        data: Yüklenen JSON verisi.
        source_file: Kaynak dosya adı.
        
    Returns:
        Document nesnelerinden oluşan bir liste.
    """
    documents = []
    
    # Döküman başlığı ve genel bilgiler
    doc_title = data.get("document_name", "")
    
    # Yönetmeliğin tamamını içeren ana metin oluşturma
    full_content = f"{doc_title}\n\n"
    
    # Yayın bilgileri varsa ekle
    if "publication_info" in data:
        pub_info = data.get("publication_info", {})
        original_pub = pub_info.get("original_publication", {})
        if original_pub:
            full_content += f"Orijinal Yayım Tarihi: {original_pub.get('date', '')}\n"
            full_content += f"Orijinal Resmî Gazete Sayısı: {original_pub.get('number', '')}\n\n"
        
        # Değişiklik bilgileri
        amendments = pub_info.get("amendments", [])
        if amendments:
            full_content += "Değişiklik Yapan Yönetmelikler:\n"
            for amendment in amendments:
                full_content += f"- Tarih: {amendment.get('date', '')}, Sayı: {amendment.get('number', '')}\n"
            full_content += "\n"
    
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
            change_info = article.get("change_info", "")
            
            # Madde başlığı
            if change_info:
                section_content += f"MADDE {article_number} – {article_title} {change_info}\n\n"
            else:
                section_content += f"MADDE {article_number} – {article_title}\n\n"
            
            # Paragrafları ekle
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
                    items = clause.get("items", [])
                    suffix = clause.get("suffix", "")
                    
                    section_content += f"{clause_letter}) {content}\n"
                    
                    for item in items:
                        section_content += f"    {item}\n"
                    
                    if suffix:
                        section_content += f"{suffix}\n\n"
                    else:
                        section_content += "\n"
            
            # Ek paragrafları ekle
            if "additional_paragraphs" in article:
                for add_paragraph in article.get("additional_paragraphs", []):
                    section_content += f"{add_paragraph}\n\n"
        
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
                "language": "tr"
            }
        ))
        
        # Ana içeriğe bölüm içeriğini ekle
        full_content += section_content
        
        # Her madde için ayrı doküman oluştur
        for article in section.get("articles", []):
            article_number = article.get("article_number", "")
            article_title = article.get("article_title", "")
            change_info = article.get("change_info", "")
            
            # Madde içeriği
            article_content = ""
            
            # Madde başlığı
            if change_info:
                article_content += f"MADDE {article_number} – {article_title} {change_info}\n\n"
            else:
                article_content += f"MADDE {article_number} – {article_title}\n\n"
            
            # Paragrafları ekle
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
                    items = clause.get("items", [])
                    suffix = clause.get("suffix", "")
                    
                    article_content += f"{clause_letter}) {content}\n"
                    
                    for item in items:
                        article_content += f"    {item}\n"
                    
                    if suffix:
                        article_content += f"{suffix}\n\n"
                    else:
                        article_content += "\n"
            
            # Ek paragrafları ekle
            if "additional_paragraphs" in article:
                for add_paragraph in article.get("additional_paragraphs", []):
                    article_content += f"{add_paragraph}\n\n"
            
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
                    "language": "tr"
                }
            ))
    
    # Tam döküman için bir Document oluştur
    full_hash = compute_hash(full_content)
    documents.append(Document(
        page_content=full_content,
        metadata={
            "hash": full_hash,
            "title": doc_title,
            "source": source_file,
            "document_type": "yonetmelik_tam",
            "language": "tr"
        }
    ))
    
    return documents