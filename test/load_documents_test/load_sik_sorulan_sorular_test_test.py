from langchain.schema import Document
import hashlib
from typing import List, Dict, Any
import json
from datetime import datetime

def compute_hash(content: str) -> str:
    """İçeriğin benzersiz hash değerini hesaplar."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Sıkça sorulan sorular JSON verisini işleyerek Document nesneleri oluşturur.
    """
    documents = []
    current_date = "2025-07-25 08:27:00"  # Verilen tarih
    user_login = "tnerler"  # Verilen kullanıcı
    
    doc_title = data.get("document_title", "")
    metadata = data.get("metadata", {})
    university_name = metadata.get("university_name", "Piri Reis Üniversitesi")
    
    # Ana doküman içeriği oluştur
    full_content = f"{doc_title}\n\n"
    
    # Her kategori için
    for category in data.get("faq_categories", []):
        category_name = category.get("category_name", "")
        questions = category.get("questions", [])
        
        full_content += f"## {category_name}\n\n"
        
        # Kategori bazlı içerik
        category_content = f"{university_name} - {category_name} ile İlgili SSS\n\n"
        
        # Her soru için
        for question in questions:
            q_id = question.get("id", "")
            q_text = question.get("question", "").replace(f"{q_id}- ", "").replace(f"{q_id}-", "")
            a_text = question.get("answer", "")
            
            full_content += f"### {q_text}\n\n{a_text}\n\n"
            category_content += f"## {q_text}\n\n{a_text}\n\n"
            
            # Soru bazlı doküman
            question_content = f"# {q_text}\n\n{a_text}\n\nKategori: {category_name}\n"
            
            documents.append(Document(
                page_content=question_content,
                metadata={
                    "hash": compute_hash(question_content),
                    "title": q_text[:50] + ("..." if len(q_text) > 50 else ""),
                    "university": university_name,
                    "category": category_name,
                    "question_id": q_id,
                    "source": source_file,
                    "document_type": "sss_soru",
                    "processed_date": current_date,
                    "processed_by": user_login
                }
            ))
        
        # Kategori dokümanı
        documents.append(Document(
            page_content=category_content,
            metadata={
                "hash": compute_hash(category_content),
                "title": f"{university_name} - {category_name} ile İlgili SSS",
                "university": university_name,
                "category": category_name,
                "source": source_file,
                "document_type": "sss_kategori",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Ana doküman
    documents.append(Document(
        page_content=full_content,
        metadata={
            "hash": compute_hash(full_content),
            "title": doc_title,
            "university": university_name,
            "source": source_file,
            "document_type": "sss_tam",
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    # Özel konulara göre rehberler oluştur
    topics = {
        "kayıt": ["kayıt", "ösym", "yerleştirme"],
        "burs": ["burs", "indirim", "ücret"],
        "eğitim": ["ingilizce", "hazırlık", "program"]
    }
    
    for topic_name, keywords in topics.items():
        topic_content = f"# {university_name} {topic_name.title()} Rehberi\n\n"
        topic_questions = []
        
        for category in data.get("faq_categories", []):
            for question in category.get("questions", []):
                combined_text = (question.get("question", "") + " " + question.get("answer", "")).lower()
                if any(keyword in combined_text for keyword in keywords):
                    topic_questions.append({
                        "question": question.get("question", "").replace(f"{question.get('id', '')}- ", ""),
                        "answer": question.get("answer", "")
                    })
        
        if topic_questions:
            for tq in topic_questions:
                topic_content += f"## {tq['question']}\n\n{tq['answer']}\n\n"
            
            documents.append(Document(
                page_content=topic_content,
                metadata={
                    "hash": compute_hash(topic_content),
                    "title": f"{university_name} {topic_name.title()} Rehberi",
                    "university": university_name,
                    "topic": topic_name,
                    "source": source_file,
                    "document_type": "sss_rehber",
                    "processed_date": current_date,
                    "processed_by": user_login
                }
            ))
    
    return documents