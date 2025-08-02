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
    Processes the Piri Reis University's Extra Examination Rights regulation JSON file
    and converts it to LangChain Document objects.
    
    Args:
        data: The loaded JSON data.
        source_file: The source file name.
        
    Returns:
        A list of Document objects.
    """
    documents = []
    
    # Document title and meta information
    doc_title = data.get("document_name", "")
    doc_date = data.get("document_date", "")
    doc_number = data.get("document_number", "")
    doc_reference = data.get("document_reference", "")
    
    # Main document information
    main_content = f"{doc_title}\n"
    if doc_date:
        main_content += f"Tarih: {doc_date}\n"
    if doc_number:
        main_content += f"Sayı: {doc_number}\n"
    if doc_reference:
        main_content += f"Referans: {doc_reference}\n\n"
    
    # Process the entire document as a single text
    full_document_content = main_content
    
    # Process sections to create documents
    for section in data.get("sections", []):
        section_name = section.get("section_name", "")
        section_title = section.get("section_title", "")
        
        section_content = f"{section_name}\n{section_title}\n\n"
        
        # Process each article in the section
        for article in section.get("articles", []):
            article_number = article.get("article_number", "")
            article_title = article.get("article_title", "")
            
            article_content = f"MADDE {article_number} - {article_title}\n\n"
            
            # Add paragraphs
            for paragraph in article.get("paragraphs", []):
                article_content += f"{paragraph}\n\n"
            
            # Add items
            if "items" in article:
                for item in article.get("items", []):
                    article_content += f"- {item}\n"
                article_content += "\n"
            
            # Add definitions
            if "definitions" in article:
                for definition in article.get("definitions", []):
                    term = definition.get("term", "")
                    
                    # Handle standard definition
                    if "definition" in definition:
                        definition_text = definition.get("definition", "")
                        article_content += f"{term}: {definition_text}\n\n"
                    
                    # Handle definition items (for "Sınırsız Sınav" type definitions with multiple items)
                    elif "definition_items" in definition:
                        article_content += f"{term}:\n"
                        for item in definition.get("definition_items", []):
                            article_content += f"- {item}\n"
                        article_content += "\n"
            
            # Add clauses (marked with letters a, b, c, etc.)
            if "clauses" in article:
                for clause in article.get("clauses", []):
                    clause_letter = clause.get("clause_letter", "")
                    content = clause.get("content", "")
                    article_content += f"{clause_letter}) {content}\n\n"
            
            # Add sub-paragraphs
            if "sub_paragraphs" in article:
                for sub_paragraph in article.get("sub_paragraphs", []):
                    article_content += f"{sub_paragraph}\n\n"
            
            section_content += article_content
        
        # Create a document for each section
        doc_hash = compute_hash(section_content)
        documents.append(Document(
            page_content=section_content,
            metadata={
                "hash": doc_hash,
                "title": doc_title,
                "section": section_name,
                "section_title": section_title,
                "document_date": doc_date,
                "document_number": doc_number,
                "source": source_file,
                "type": "regulation_section"
            }
        ))
        
        # Add to main content
        full_document_content += section_content
    
    # Add approval information
    if "approval_info" in data:
        approval = data.get("approval_info", {})
        approval_content = f"\n\n{approval.get('title', '')}\n"
        approval_content += f"Karar Tarihi: {approval.get('decision_date', '')}\n"
        approval_content += f"Karar Sayısı: {approval.get('decision_number', '')}\n"
        
        full_document_content += approval_content
    
    # Create document for the full document
    doc_hash = compute_hash(full_document_content)
    documents.append(Document(
        page_content=full_document_content,
        metadata={
            "hash": doc_hash,
            "title": doc_title,
            "document_date": doc_date,
            "document_number": doc_number,
            "document_reference": doc_reference,
            "section": "full_document",
            "source": source_file,
            "type": "regulation_full"
        }
    ))
    
    # Create separate document for each article
    for section in data.get("sections", []):
        section_name = section.get("section_name", "")
        section_title = section.get("section_title", "")
        
        for article in section.get("articles", []):
            article_number = article.get("article_number", "")
            article_title = article.get("article_title", "")
            
            article_content = f"MADDE {article_number} - {article_title}\n\n"
            
            # Add paragraphs
            for paragraph in article.get("paragraphs", []):
                article_content += f"{paragraph}\n\n"
            
            # Add items
            if "items" in article:
                for item in article.get("items", []):
                    article_content += f"- {item}\n"
                article_content += "\n"
            
            # Add definitions
            if "definitions" in article:
                for definition in article.get("definitions", []):
                    term = definition.get("term", "")
                    
                    # Handle standard definition
                    if "definition" in definition:
                        definition_text = definition.get("definition", "")
                        article_content += f"{term}: {definition_text}\n\n"
                    
                    # Handle definition items (for "Sınırsız Sınav" type definitions with multiple items)
                    elif "definition_items" in definition:
                        article_content += f"{term}:\n"
                        for item in definition.get("definition_items", []):
                            article_content += f"- {item}\n"
                        article_content += "\n"
            
            # Add clauses (marked with letters a, b, c, etc.)
            if "clauses" in article:
                for clause in article.get("clauses", []):
                    clause_letter = clause.get("clause_letter", "")
                    content = clause.get("content", "")
                    article_content += f"{clause_letter}) {content}\n\n"
            
            # Add sub-paragraphs
            if "sub_paragraphs" in article:
                for sub_paragraph in article.get("sub_paragraphs", []):
                    article_content += f"{sub_paragraph}\n\n"
            
            # Create document for each article
            doc_hash = compute_hash(article_content)
            documents.append(Document(
                page_content=article_content,
                metadata={
                    "hash": doc_hash,
                    "title": doc_title,
                    "section": section_name,
                    "section_title": section_title,
                    "article_number": article_number,
                    "article_title": article_title,
                    "document_date": doc_date,
                    "document_number": doc_number,
                    "source": source_file,
                    "type": "regulation_article"
                }
            ))
    
    return documents
