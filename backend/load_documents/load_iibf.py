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
    Processes faculty JSON structure and extracts meaningful content.
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
                
                # Handle mission-vision format
                elif "title" in section_value and ("vision" in section_value or "mission" in section_value):
                    title = section_value["title"]
                    vision = section_value.get("vision", "")
                    mission = section_value.get("mission", "")
                    
                    content = f"Vizyon:\n{vision}\n\nMisyon:\n{mission}" if vision and mission else (
                        f"Vizyon:\n{vision}" if vision else f"Misyon:\n{mission}"
                    )
                    
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
                
                # Handle section with heads (like department heads)
                elif "title" in section_value and "heads" in section_value:
                    title = section_value["title"]
                    heads_text = "\n".join([f"{head.get('name', '')}: {head.get('department', '')}" 
                                         for head in section_value["heads"]])
                    text = f"{faculty_name} - {title}\n\n{heads_text}"
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
    
    # Process academic staff if it exists at the faculty level
    if "academic_staff" in data and isinstance(data["academic_staff"], dict):
        staff_by_dept = data["academic_staff"].get("departments", {})
        for dept_key, staff_list in staff_by_dept.items():
            dept_name = dept_key.replace("_", " ").title()
            staff_text = "\n".join([f"{staff.get('rank', '')} {staff.get('name', '')}" for staff in staff_list])
            text = f"{faculty_name} - {dept_name} - Akademik Kadro\n\n{staff_text}"
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
                    title = dept_value["department_head_message"].get("title", "Bölüm Başkanının Mesajı")
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
                staff_text = "\n".join([staff.get("name", "") for staff in dept_value["academic_staff"]])
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
            
            # Why choose this department
            if "why_choose" in dept_value and isinstance(dept_value["why_choose"], dict):
                title = dept_value["why_choose"].get("title", "Neden Bu Bölüm")
                content = dept_value["why_choose"].get("content", "")
                text = f"{faculty_name} - {dept_name}\n\n{title}:\n{content}"
                doc_hash = compute_hash(text)
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "hash": doc_hash,
                        "faculty": faculty_name,
                        "department": dept_name,
                        "section": "why_choose",
                        "source": source_file
                    }
                ))
            
            # Student profile
            if "student_profile" in dept_value and isinstance(dept_value["student_profile"], dict):
                title = dept_value["student_profile"].get("title", "Öğrenci Profili")
                targets = dept_value["student_profile"].get("targets", [])
                content = "\n- " + "\n- ".join(targets) if targets else ""
                text = f"{faculty_name} - {dept_name}\n\n{title}:{content}"
                doc_hash = compute_hash(text)
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "hash": doc_hash,
                        "faculty": faculty_name,
                        "department": dept_name,
                        "section": "student_profile",
                        "source": source_file
                    }
                ))
            
            # Career opportunities
            if "career_opportunities" in dept_value and isinstance(dept_value["career_opportunities"], dict):
                title = dept_value["career_opportunities"].get("title", "Kariyer Fırsatları")
                opportunities = dept_value["career_opportunities"].get("opportunities", [])
                content = "\n- " + "\n- ".join(opportunities) if opportunities else ""
                text = f"{faculty_name} - {dept_name}\n\n{title}:{content}"
                doc_hash = compute_hash(text)
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "hash": doc_hash,
                        "faculty": faculty_name,
                        "department": dept_name,
                        "section": "career_opportunities",
                        "source": source_file
                    }
                ))
            
            # Dual major minor
            if "dual_major_minor" in dept_value and isinstance(dept_value["dual_major_minor"], dict):
                dual_major = dept_value["dual_major_minor"].get("dual_major", {})
                minor = dept_value["dual_major_minor"].get("minor", {})
                
                dual_major_content = ""
                if dual_major:
                    dual_major_title = dual_major.get("title", "Çift Anadal")
                    dual_major_text = dual_major.get("content", "")
                    dual_major_content = f"{dual_major_title}:\n{dual_major_text}\n\n"
                
                minor_content = ""
                if minor:
                    minor_title = minor.get("title", "Yandal")
                    minor_text = minor.get("content", "")
                    minor_content = f"{minor_title}:\n{minor_text}"
                
                text = f"{faculty_name} - {dept_name}\n\nÇift Anadal ve Yandal Programları:\n\n{dual_major_content}{minor_content}"
                doc_hash = compute_hash(text)
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "hash": doc_hash,
                        "faculty": faculty_name,
                        "department": dept_name,
                        "section": "dual_major_minor",
                        "source": source_file
                    }
                ))
            
            # Erasmus
            if "erasmus" in dept_value:
                if isinstance(dept_value["erasmus"], dict):
                    title = dept_value["erasmus"].get("title", "Erasmus")
                    content = dept_value["erasmus"].get("content", "")
                    text = f"{faculty_name} - {dept_name}\n\n{title}:\n{content}"
                elif isinstance(dept_value["erasmus"], str):
                    text = f"{faculty_name} - {dept_name}\n\nErasmus:\n{dept_value['erasmus']}"
                
                doc_hash = compute_hash(text)
                documents.append(Document(
                    page_content=text,
                    metadata={
                        "hash": doc_hash,
                        "faculty": faculty_name,
                        "department": dept_name,
                        "section": "erasmus",
                        "source": source_file
                    }
                ))
    
    return documents
