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

def process_data(data: Dict[str, Any], source_file: str) -> List[Document]:
    """
    Process JSON structure for educational programs like Hybrid and Electric Vehicles Technology.
    Extracts meaningful content and organizes it into searchable documents.
    """
    documents = []
    program_name = data.get("program_name", "")
    
    # Main program information document
    main_content = f"Program: {program_name}\n\n"
    
    # Process sections
    if "sections" in data:
        # Education section
        if "education" in data["sections"]:
            education = data["sections"]["education"]
            if "title" in education and "content" in education:
                edu_content = education["content"]
                main_content += f"{education['title']}:\n{edu_content}\n\n"
                
                # Create a separate document for education info
                text = f"{program_name} - {education['title']}\n\n{edu_content}"
                doc_hash = compute_hash(text)
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "hash": doc_hash,
                        "program": program_name,
                        "section": "education",
                        "source": source_file
                    }
                ))
            
            # Vertical transfer opportunities
            if "vertical_transfer" in education and isinstance(education["vertical_transfer"], dict):
                vertical = education["vertical_transfer"]
                v_title = vertical.get("title", "Dikey Geçiş İmkanları")
                v_content = vertical.get("content", "")
                
                available_programs = vertical.get("available_programs", [])
                programs_text = ""
                if available_programs:
                    programs_text = "- " + "\n- ".join(available_programs)
                
                completion = vertical.get("completion", "")
                
                v_text = f"{v_content}\n\n{programs_text}\n\n{completion}"
                text = f"{program_name} - {v_title}\n\n{v_text}"
                doc_hash = compute_hash(text)
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "hash": doc_hash,
                        "program": program_name,
                        "section": "vertical_transfer",
                        "source": source_file
                    }
                ))
                
                main_content += f"{v_title}:\n{v_text}\n\n"
        
        # Career opportunities section
        if "career_opportunities" in data["sections"]:
            career = data["sections"]["career_opportunities"]
            if "title" in career and "content" in career:
                career_content = career["content"]
                
                # Add positions information if available
                positions_text = ""
                if "positions" in career and isinstance(career["positions"], list):
                    for position in career["positions"]:
                        positions_text += f"\n• {position.get('title', '')}"
                        
                        if "sector" in position:
                            positions_text += f" - {position['sector']}"
                        
                        if "sectors" in position:
                            sectors = position.get("sectors", [])
                            sectors_text = ", ".join(sectors)
                            positions_text += f" - Sektörler: {sectors_text}"
                
                career_full_text = f"{career_content}{positions_text}"
                text = f"{program_name} - {career['title']}\n\n{career_full_text}"
                doc_hash = compute_hash(text)
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "hash": doc_hash,
                        "program": program_name,
                        "section": "career_opportunities",
                        "source": source_file
                    }
                ))
                
                main_content += f"{career['title']}:\n{career_full_text}\n\n"
        
        # Certifications section
        if "certifications" in data["sections"]:
            certifications = data["sections"]["certifications"]
            cert_title = "Sertifikasyonlar ve Uyumluluk"
            
            compliance_text = ""
            if "compliance" in certifications and isinstance(certifications["compliance"], list):
                compliance_text = "Program aşağıdaki standartlara uyumludur:\n- "
                compliance_text += "\n- ".join(certifications["compliance"])
            
            text = f"{program_name} - {cert_title}\n\n{compliance_text}"
            doc_hash = compute_hash(text)
            documents.append(Document(
                page_content=text,
                metadata={
                    "hash": doc_hash,
                    "program": program_name,
                    "section": "certifications",
                    "source": source_file
                }
            ))
            
            main_content += f"{cert_title}:\n{compliance_text}\n\n"
        
        # Degree information
        if "degree" in data["sections"]:
            degree = data["sections"]["degree"]
            degree_title = "Program Derecesi"
            
            degree_text = f"Derece Türü: {degree.get('type', '')}\n"
            degree_text += f"Verilen Unvan: {degree.get('title', '')}"
            
            text = f"{program_name} - {degree_title}\n\n{degree_text}"
            doc_hash = compute_hash(text)
            documents.append(Document(
                page_content=text,
                metadata={
                    "hash": doc_hash,
                    "program": program_name,
                    "section": "degree",
                    "source": source_file
                }
            ))
            
            main_content += f"{degree_title}:\n{degree_text}\n\n"
        
        # Focus areas
        if "focus_areas" in data["sections"]:
            focus_areas = data["sections"]["focus_areas"]
            focus_title = "Odak Alanları"
            
            focus_text = ""
            if isinstance(focus_areas, list):
                focus_text = "- " + "\n- ".join(focus_areas)
            
            text = f"{program_name} - {focus_title}\n\n{focus_text}"
            doc_hash = compute_hash(text)
            documents.append(Document(
                page_content=text,
                metadata={
                    "hash": doc_hash,
                    "program": program_name,
                    "section": "focus_areas",
                    "source": source_file
                }
            ))
            
            main_content += f"{focus_title}:\n{focus_text}\n\n"
    
    # Create a comprehensive document for the entire program
    doc_hash = compute_hash(main_content)
    documents.append(Document(
        page_content=main_content,
        metadata={
            "hash": doc_hash,
            "program": program_name,
            "section": "complete_program",
            "source": source_file
        }
    ))
    
    return documents