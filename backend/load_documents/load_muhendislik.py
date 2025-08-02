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
    Recursively processes the faculty JSON structure and extracts meaningful content.
    """
    documents = []
    faculty_name = data.get("faculty_name", "")
    
    # Process sections
    if "sections" in data:
        for section_key, section_value in data["sections"].items():
            if isinstance(section_value, dict):
                # Handle section with title and content
                if "title" in section_value and "content" in section_value:
                    title = section_value["title"]
                    content = section_value["content"]
                    if content:  # Skip empty content
                        text = f"{faculty_name} - {title}\n\n{content}"
                        doc_hash = compute_hash(text)
                        documents.append(Document(
                            page_content=text,
                            metadata={
                                "hash": doc_hash,
                                "faculty": faculty_name,
                                "section": section_key,
                                "source": source_file
                            }
                        ))
                
                # Handle section with members (like faculty management)
                elif "title" in section_value and "members" in section_value:
                    title = section_value["title"]
                    members_text = "\n".join([f"{member.get('name', '')}: {member.get('title', '')}" 
                                           for member in section_value["members"]])
                    text = f"{faculty_name} - {title}\n\n{members_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "section": section_key,
                            "source": source_file
                        }
                    ))
    
    # Process departments
    if "departments" in data:
        for dept_key, dept_value in data["departments"].items():
            dept_name = dept_value.get("name", "")
            
            # Department about section
            if "about" in dept_value and isinstance(dept_value["about"], str):
                text = f"{faculty_name} - {dept_name}\n\nHakkında:\n{dept_value['about']}"
                doc_hash = compute_hash(text)
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "hash": doc_hash,
                        "faculty": faculty_name,
                        "department": dept_name,
                        "section": "about",
                        "source": source_file
                    }
                ))
            
            # Department head message
            if "department_head_message" in dept_value:
                if isinstance(dept_value["department_head_message"], str):
                    head_message = dept_value["department_head_message"]
                elif isinstance(dept_value["department_head_message"], dict):
                    head_message = dept_value["department_head_message"].get("content", "")
                
                if head_message:
                    text = f"{faculty_name} - {dept_name}\n\nBölüm Başkanı Mesajı:\n{head_message}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "department": dept_name,
                            "section": "department_head_message",
                            "source": source_file
                        }
                    ))
            
            # Academic staff
            if "academic_staff" in dept_value and isinstance(dept_value["academic_staff"], list):
                staff_text = "\n".join([member.get("name", "") for member in dept_value["academic_staff"]])
                text = f"{faculty_name} - {dept_name}\n\nAkademik Kadro:\n{staff_text}"
                doc_hash = compute_hash(text)
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "hash": doc_hash,
                        "faculty": faculty_name,
                        "department": dept_name,
                        "section": "academic_staff",
                        "source": source_file
                    }
                ))
            
            # Internship information
            if "internship" in dept_value:
                if isinstance(dept_value["internship"], dict):
                    internship_text = f"Toplam Staj Süresi: {dept_value['internship'].get('total_days', '')} gün\n\n"
                    for group in dept_value["internship"].get("groups", []):
                        internship_text += f"{group.get('name', '')}: {group.get('description', '')}\n\n"
                    
                    text = f"{faculty_name} - {dept_name}\n\nStaj Bilgileri:\n{internship_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "department": dept_name,
                            "section": "internship",
                            "source": source_file
                        }
                    ))
            
            # Other sections specific to departments
            for key in ["events", "minor_program", "student_clubs", "erasmus", "graduate_programs"]:
                if key in dept_value:
                    if isinstance(dept_value[key], dict):
                        if "content" in dept_value[key]:
                            content = dept_value[key]["content"]
                        else:
                            content = json.dumps(dept_value[key], ensure_ascii=False, indent=2)
                    elif isinstance(dept_value[key], str):
                        content = dept_value[key]
                    else:
                        content = json.dumps(dept_value[key], ensure_ascii=False, indent=2)
                    
                    text = f"{faculty_name} - {dept_name}\n\n{key.replace('_', ' ').title()}:\n{content}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "department": dept_name,
                            "section": key,
                            "source": source_file
                        }
                    ))
    
    return documents
