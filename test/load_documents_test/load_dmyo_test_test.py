import json
from langchain.schema import Document
import hashlib
import os
from typing import List, Dict, Any, Union
import glob


def compute_hash(content: str) -> str:
    """
    Computes a SHA256 hash from content to prevent duplicate document loading.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def safe_get(obj: Union[Dict, Any], key: str, default: Any = "") -> Any:
    """
    Safely get a value from a dictionary, or return default if obj is not a dict
    or key doesn't exist.
    """
    if isinstance(obj, dict) and key in obj:
        return obj[key]
    return default

def process_data(data: Dict[str, Any], source_file: str) -> List[Document]:
    """
    Process the JSON structure for the Maritime Vocational School (DMYO).
    Extracts meaningful content and organizes it into searchable documents.
    """
    documents = []
    school_name = safe_get(data, "school_name", "")
    
    # Process general sections about the school
    if "sections" in data:
        sections = data["sections"]
        
        # About section with director message
        if "about" in sections and isinstance(sections["about"], dict):
            about = sections["about"]
            
            # Director message
            if "director_message" in about and isinstance(about["director_message"], dict):
                dir_msg = about["director_message"]
                title = safe_get(dir_msg, "title", "Müdür Mesajı")
                content = safe_get(dir_msg, "content", "")
                
                if content:
                    text = f"{school_name} - {title}\n\n{content}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "section": "director_message",
                            "source": source_file
                        }
                    ))
            
            # History section
            if "history" in about and isinstance(about["history"], dict):
                history = about["history"]
                title = safe_get(history, "title", "Tarihçe")
                content = safe_get(history, "content", "")
                
                if content:
                    text = f"{school_name} - {title}\n\n{content}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "section": "history",
                            "source": source_file
                        }
                    ))
            
            # Mission vision section
            if "mission_vision" in about and isinstance(about["mission_vision"], dict):
                mission_vision = about["mission_vision"]
                title = safe_get(mission_vision, "title", "Misyon-Vizyon")
                content = safe_get(mission_vision, "content", "")
                
                if content:
                    text = f"{school_name} - {title}\n\n{content}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "section": "mission_vision",
                            "source": source_file
                        }
                    ))
            
            # Other about sections
            for key in ["quality", "research", "internationalization"]:
                if key in about and isinstance(about[key], dict):
                    section = about[key]
                    title = safe_get(section, "title", key.capitalize())
                    content = safe_get(section, "content", "")
                    
                    if content:
                        text = f"{school_name} - {title}\n\n{content}"
                        doc_hash = compute_hash(text)
                        documents.append(Document(
                            page_content=text,
                            metadata={
                                "hash": doc_hash,
                                "school": school_name,
                                "section": key,
                                "source": source_file
                            }
                        ))
        
        # Management sections
        if "management" in sections and isinstance(sections["management"], dict):
            management = sections["management"]
            
            # School management
            if "school_management" in management and isinstance(management["school_management"], dict):
                mgmt = management["school_management"]
                title = safe_get(mgmt, "title", "Yüksekokulu Yönetimi")
                members = safe_get(mgmt, "members", [])
                
                if members and isinstance(members, list):
                    members_text = "\n".join([
                        f"{safe_get(m, 'name', '')}: {safe_get(m, 'title', '')}" 
                        for m in members if isinstance(m, dict)
                    ])
                    text = f"{school_name} - {title}\n\n{members_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "section": "school_management",
                            "source": source_file
                        }
                    ))
            
            # School board
            if "school_board" in management and isinstance(management["school_board"], dict):
                board = management["school_board"]
                title = safe_get(board, "title", "Yüksekokul Kurulu")
                members = safe_get(board, "members", [])
                
                if members and isinstance(members, list):
                    members_text = "\n".join([
                        f"{safe_get(m, 'name', '')}: {safe_get(m, 'title', '')}" 
                        for m in members if isinstance(m, dict)
                    ])
                    text = f"{school_name} - {title}\n\n{members_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "section": "school_board",
                            "source": source_file
                        }
                    ))
            
            # Executive board
            if "executive_board" in management and isinstance(management["executive_board"], dict):
                exec_board = management["executive_board"]
                title = safe_get(exec_board, "title", "Yüksekokul Yönetim Kurulu")
                members = safe_get(exec_board, "members", [])
                
                if members and isinstance(members, list):
                    members_text = "\n".join([
                        f"{safe_get(m, 'name', '')}: {safe_get(m, 'title', '')}" 
                        for m in members if isinstance(m, dict)
                    ])
                    text = f"{school_name} - {title}\n\n{members_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "section": "executive_board",
                            "source": source_file
                        }
                    ))
            
            # Department and program heads
            if "department_program_heads" in management and isinstance(management["department_program_heads"], dict):
                dept_heads = management["department_program_heads"]
                title = safe_get(dept_heads, "title", "Bölüm Başkanları ve Program Başkanları Sorumluları")
                departments = safe_get(dept_heads, "departments", [])
                
                if departments and isinstance(departments, list):
                    dept_text = ""
                    for dept in departments:
                        if not isinstance(dept, dict):
                            continue
                            
                        dept_text += f"Bölüm: {safe_get(dept, 'name', '')}\n"
                        dept_text += f"Bölüm Başkanı: {safe_get(dept, 'head', '')}\n"
                        
                        if "programs" in dept and isinstance(dept["programs"], list):
                            dept_text += "Programlar:\n"
                            for prog in dept["programs"]:
                                if isinstance(prog, dict):
                                    dept_text += f"- {safe_get(prog, 'name', '')}: {safe_get(prog, 'responsible', '')}\n"
                        dept_text += "\n"
                    
                    text = f"{school_name} - {title}\n\n{dept_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "section": "department_program_heads",
                            "source": source_file
                        }
                    ))
        
        # Academic staff by department
        if "academic_staff" in sections and isinstance(sections["academic_staff"], dict):
            ac_staff = sections["academic_staff"]
            title = safe_get(ac_staff, "title", "Akademik Kadro")
            
            if "departments" in ac_staff and isinstance(ac_staff["departments"], dict):
                depts = ac_staff["departments"]
                
                for dept_key, dept_value in depts.items():
                    if not isinstance(dept_value, dict):
                        continue
                        
                    dept_name = safe_get(dept_value, "name", dept_key)
                    
                    if "programs" in dept_value and isinstance(dept_value["programs"], dict):
                        programs = dept_value["programs"]
                        
                        for prog_key, prog_value in programs.items():
                            if not isinstance(prog_value, dict):
                                continue
                                
                            prog_name = safe_get(prog_value, "name", prog_key)
                            staff = safe_get(prog_value, "staff", [])
                            
                            if staff and isinstance(staff, list):
                                staff_text = "\n".join([
                                    f"{safe_get(s, 'rank', '')} {safe_get(s, 'name', '')}" 
                                    for s in staff if isinstance(s, dict)
                                ])
                                text = f"{school_name} - {dept_name} - {prog_name} - Akademik Kadro\n\n{staff_text}"
                                doc_hash = compute_hash(text)
                                documents.append(Document(
                                    page_content=text,
                                    metadata={
                                        "hash": doc_hash,
                                        "school": school_name,
                                        "department": dept_name,
                                        "program": prog_name,
                                        "section": "academic_staff",
                                        "source": source_file
                                    }
                                ))
    
    # Process individual programs
    if "programs" in data and isinstance(data["programs"], dict):
        programs = data["programs"]
        
        for prog_key, prog_value in programs.items():
            if not isinstance(prog_value, dict):
                continue
                
            prog_name = safe_get(prog_value, "name", prog_key)
            
            # Program about section
            if "about" in prog_value and isinstance(prog_value["about"], dict):
                about = prog_value["about"]
                title = safe_get(about, "title", "Program Hakkında")
                
                # Main content
                content = safe_get(about, "content", "")
                if content:
                    # Check for career_opportunities and vertical_transfer in content
                    career_content = safe_get(about, "career_opportunities", "")
                    
                    # Combine all content
                    full_content = content
                    if career_content:
                        full_content += f"\n\nKariyer Fırsatları:\n{career_content}"
                    
                    # Vertical transfer section
                    if "vertical_transfer" in about and isinstance(about["vertical_transfer"], dict):
                        vt = about["vertical_transfer"]
                        vt_title = safe_get(vt, "title", "Dikey Geçiş İmkanları")
                        vt_content = safe_get(vt, "content", "")
                        vt_programs = safe_get(vt, "programs", [])
                        vt_additional = safe_get(vt, "additional_info", "")
                        
                        vt_text = f"{vt_title}:\n{vt_content}\n"
                        if vt_programs and isinstance(vt_programs, list):
                            vt_text += "- " + "\n- ".join(vt_programs) + "\n"
                        if vt_additional:
                            vt_text += vt_additional
                        
                        full_content += f"\n\n{vt_text}"
                    
                    text = f"{school_name} - {prog_name} - {title}\n\n{full_content}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "program": prog_name,
                            "section": "about",
                            "source": source_file
                        }
                    ))
            
            # Program head message
            if "program_head_message" in prog_value and isinstance(prog_value["program_head_message"], dict):
                head_msg = prog_value["program_head_message"]
                title = safe_get(head_msg, "title", "Program Sorumlusunun Mesajı")
                content = safe_get(head_msg, "content", "")
                author = safe_get(head_msg, "author", "")
                author_title = safe_get(head_msg, "title_author", "")
                
                if content:
                    message_text = content
                    if author:
                        message_text += f"\n\n{author}"
                    if author_title:
                        message_text += f"\n{author_title}"
                    
                    text = f"{school_name} - {prog_name} - {title}\n\n{message_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "program": prog_name,
                            "section": "program_head_message",
                            "source": source_file
                        }
                    ))
            
            # Academic staff
            if "academic_staff" in prog_value:
                staff = prog_value["academic_staff"]
                
                if staff and isinstance(staff, list):
                    staff_text = "\n".join([safe_get(s, "name", "") for s in staff if isinstance(s, dict)])
                    text = f"{school_name} - {prog_name} - Akademik Kadro\n\n{staff_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "program": prog_name,
                            "section": "academic_staff",
                            "source": source_file
                        }
                    ))
            
            # Other program sections
            for section_key in ["internship", "dual_major_minor", "student_clubs", "erasmus", "events", "news"]:
                if section_key in prog_value:
                    section = prog_value[section_key]
                    
                    if isinstance(section, dict):
                        title = safe_get(section, "title", section_key.replace("_", " ").capitalize())
                        content = safe_get(section, "content", "")
                        
                        if content:
                            text = f"{school_name} - {prog_name} - {title}\n\n{content}"
                            doc_hash = compute_hash(text)
                            documents.append(Document(
                                page_content=text,
                                metadata={
                                    "hash": doc_hash,
                                    "school": school_name,
                                    "program": prog_name,
                                    "section": section_key,
                                    "source": source_file
                                }
                            ))
            
            # Special case for Hybrid and Electric Vehicles program (inactive)
            if "note" in prog_value:
                note = safe_get(prog_value, "note", "")
                
                if note:
                    text = f"{school_name} - {prog_name}\n\nNot: {note}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "school": school_name,
                            "program": prog_name,
                            "section": "note",
                            "source": source_file
                        }
                    ))
    
    # Process contact information
    if "contact" in data and isinstance(data["contact"], dict):
        contact = data["contact"]
        title = safe_get(contact, "title", "İletişim")
        content = safe_get(contact, "content", "")
        
        if content:
            text = f"{school_name} - {title}\n\n{content}"
            doc_hash = compute_hash(text)
            documents.append(Document(
                page_content=text,
                metadata={
                    "hash": doc_hash,
                    "school": school_name,
                    "section": "contact",
                    "source": source_file
                }
            ))
    
    return documents