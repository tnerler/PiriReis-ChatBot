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
    Processes faculty JSON structure specifically for the hukuk.json format
    and extracts meaningful content.
    """
    documents = []
    faculty_name = data.get("faculty_name", "")
    
    # Process general sections
    if "sections" in data:
        for section_key, section_value in data["sections"].items():
            # Basic sections with title and content
            if isinstance(section_value, dict) and "title" in section_value and "content" in section_value:
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
            
            # Individual mission/vision sections
            elif section_key in ["mission", "vision"] and isinstance(section_value, dict):
                title = section_value.get("title", section_key.capitalize())
                content = section_value.get("content", "")
                if content:
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
            
            # Faculty management members
            elif section_key in ["management", "faculty_board", "faculty_admin_board"] and isinstance(section_value, dict):
                title = section_value.get("title", "")
                if "members" in section_value and isinstance(section_value["members"], list):
                    members_text = ""
                    for member in section_value["members"]:
                        member_info = f"{member.get('name', '')}: {member.get('title', '')}"
                        if "email" in member and "phone" in member:
                            member_info += f" ({member.get('email', '')}, {member.get('phone', '')})"
                        members_text += member_info + "\n"
                    
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
            
            # Department heads
            elif section_key == "department_heads" and isinstance(section_value, dict):
                title = section_value.get("title", "Bölüm Başkanları")
                if "heads" in section_value and isinstance(section_value["heads"], list):
                    heads_text = ""
                    for head in section_value["heads"]:
                        head_info = f"{head.get('name', '')}: {head.get('department', '')}"
                        if "email" in head and "phone" in head:
                            head_info += f" ({head.get('email', '')}, {head.get('phone', '')})"
                        heads_text += head_info + "\n"
                    
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
            
            # Committees and commissions
            elif section_key == "committees" and isinstance(section_value, dict):
                main_title = section_value.get("title", "Komisyon ve Kurullar")
                
                # Process each committee group
                for committee_key, committee_value in section_value.items():
                    if isinstance(committee_value, dict) and committee_key not in ["title"]:
                        title = committee_value.get("title", "")
                        content = ""
                        
                        if "committees" in committee_value and isinstance(committee_value["committees"], list):
                            content = "- " + "\n- ".join(committee_value["committees"])
                        elif "commissions" in committee_value and isinstance(committee_value["commissions"], list):
                            content = "- " + "\n- ".join(committee_value["commissions"])
                        
                        if content:
                            text = f"{faculty_name} - {main_title} - {title}\n\n{content}"
                            doc_hash = compute_hash(text)
                            documents.append(Document(
                                page_content=text,
                                metadata={
                                    "hash": doc_hash,
                                    "faculty": faculty_name,
                                    "section": f"{section_key}_{committee_key}",
                                    "source": source_file
                                }
                            ))
    
    # Process academic staff
    if "academic_staff" in data:
        for dept_key, dept_value in data["academic_staff"].items():
            if isinstance(dept_value, dict) and "title" in dept_value and "members" in dept_value:
                title = dept_value["title"]
                members = dept_value["members"]
                
                if isinstance(members, list):
                    members_text = ""
                    
                    # Handle different member formats
                    if all(isinstance(m, str) for m in members):
                        # Simple list of names
                        members_text = "\n".join(members)
                    else:
                        # Detailed member info
                        for member in members:
                            if isinstance(member, dict):
                                member_info = member.get("name", "")
                                if "title" in member:
                                    member_info += f": {member.get('title', '')}"
                                if "email" in member and "phone" in member:
                                    member_info += f" ({member.get('email', '')}, {member.get('phone', '')})"
                                members_text += member_info + "\n"
                    
                    text = f"{faculty_name} - {title}\n\n{members_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "department": dept_key,
                            "section": "academic_staff",
                            "source": source_file
                        }
                    ))
    
    # Process departments
    if "departments" in data:
        for dept_key, dept_value in data["departments"].items():
            dept_name = dept_value.get("name", "")
            
            # Process sub-departments
            for subdept_key, subdept_value in dept_value.items():
                # Skip the name field
                if subdept_key == "name":
                    continue
                
                if isinstance(subdept_value, dict):
                    # Department head message
                    if "department_head_message" in subdept_value:
                        title = subdept_value.get("title", subdept_key)
                        message = subdept_value["department_head_message"]
                        text = f"{faculty_name} - {dept_name} - {title}\n\nBölüm Başkanı Mesajı:\n{message}"
                        doc_hash = compute_hash(text)
                        documents.append(Document(
                            page_content=text,
                            metadata={
                                "hash": doc_hash,
                                "faculty": faculty_name,
                                "department": dept_name,
                                "subdepartment": subdept_key,
                                "section": "department_head_message",
                                "source": source_file
                            }
                        ))
                    
                    # Dual major programs
                    elif subdept_key == "dual_major" and "content" in subdept_value:
                        title = subdept_value.get("title", "Çift Anadal Programı")
                        content = subdept_value["content"]
                        text = f"{faculty_name} - {dept_name}\n\n{title}:\n{content}"
                        doc_hash = compute_hash(text)
                        documents.append(Document(
                            page_content=text,
                            metadata={
                                "hash": doc_hash,
                                "faculty": faculty_name,
                                "department": dept_name,
                                "section": "dual_major",
                                "source": source_file
                            }
                        ))
                    
                    # Student clubs
                    elif subdept_key == "student_clubs":
                        title = subdept_value.get("title", "Öğrenci Kulüpleri")
                        content = subdept_value.get("content", "")
                        clubs_text = content + "\n\n"
                        
                        if "clubs" in subdept_value and isinstance(subdept_value["clubs"], list):
                            for club in subdept_value["clubs"]:
                                club_text = f"{club.get('name', '')}\n"
                                club_text += f"Kuruluş: {club.get('founded', '')}\n"
                                club_text += f"Üye Sayısı: {club.get('members', '')}\n"
                                club_text += f"Danışman: {club.get('advisor', '')}\n"
                                club_text += f"Açıklama: {club.get('description', '')}\n"
                                if "achievements" in club:
                                    club_text += f"Başarılar: {club.get('achievements', '')}\n"
                                clubs_text += club_text + "\n"
                        
                        text = f"{faculty_name} - {dept_name}\n\n{title}:\n{clubs_text}"
                        doc_hash = compute_hash(text)
                        documents.append(Document(
                            page_content=text,
                            metadata={
                                "hash": doc_hash,
                                "faculty": faculty_name,
                                "department": dept_name,
                                "section": "student_clubs",
                                "source": source_file
                            }
                        ))
                    
                    # Erasmus information
                    elif subdept_key == "erasmus":
                        title = subdept_value.get("title", "Erasmus")
                        content = subdept_value.get("content", "")
                        partners_text = ""
                        
                        if "partner_universities" in subdept_value and isinstance(subdept_value["partner_universities"], list):
                            partners_text = "\nPartner Üniversiteler:\n- "
                            partners_text += "\n- ".join(subdept_value["partner_universities"])
                        
                        text = f"{faculty_name} - {dept_name}\n\n{title}:\n{content}{partners_text}"
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
                    
                    # Graduate programs
                    elif subdept_key == "graduate":
                        title = subdept_value.get("title", "Lisansüstü Programlar")
                        programs_text = ""
                        
                        if "programs" in subdept_value and isinstance(subdept_value["programs"], list):
                            for program in subdept_value["programs"]:
                                program_text = f"{program.get('name', '')}\n"
                                program_text += f"Anabilim Dalı: {program.get('department', '')}\n"
                                program_text += f"Kuruluş: {program.get('established', '')}\n"
                                program_text += f"Başlangıç: {program.get('start_date', '')}\n"
                                programs_text += program_text + "\n"
                        
                        text = f"{faculty_name} - {dept_name}\n\n{title}:\n{programs_text}"
                        doc_hash = compute_hash(text)
                        documents.append(Document(
                            page_content=text,
                            metadata={
                                "hash": doc_hash,
                                "faculty": faculty_name,
                                "department": dept_name,
                                "section": "graduate",
                                "source": source_file
                            }
                        ))
                    
                    # Contact information
                    elif subdept_key == "contact":
                        title = subdept_value.get("title", "İletişim")
                        address = subdept_value.get("address", "")
                        email = subdept_value.get("email", "")
                        phone = subdept_value.get("phone", "")
                        fax = subdept_value.get("fax", "")
                        
                        contact_text = f"Adres: {address}\n"
                        contact_text += f"E-posta: {email}\n"
                        contact_text += f"Telefon: {phone}\n"
                        contact_text += f"Faks: {fax}\n"
                        
                        text = f"{faculty_name} - {dept_name}\n\n{title}:\n{contact_text}"
                        doc_hash = compute_hash(text)
                        documents.append(Document(
                            page_content=text,
                            metadata={
                                "hash": doc_hash,
                                "faculty": faculty_name,
                                "department": dept_name,
                                "section": "contact",
                                "source": source_file
                            }
                        ))
                    
                    # Academic program sections
                    elif subdept_key == "academic_program" and "sections" in subdept_value:
                        title = "Akademik Program"
                        sections_text = "- " + "\n- ".join(subdept_value["sections"])
                        
                        text = f"{faculty_name} - {dept_name}\n\n{title}:\n{sections_text}"
                        doc_hash = compute_hash(text)
                        documents.append(Document(
                            page_content=text,
                            metadata={
                                "hash": doc_hash,
                                "faculty": faculty_name,
                                "department": dept_name,
                                "section": "academic_program",
                                "source": source_file
                            }
                        ))
    
    return documents