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
    Process Maritime Faculty (Denizcilik Fakültesi) JSON structure and extract meaningful content.
    Organizes content into searchable documents with appropriate metadata.
    """
    documents = []
    faculty_name = data.get("faculty_name", "")
    
    # Process general faculty sections
    if "sections" in data:
        sections = data["sections"]
        
        # About section
        if "about" in sections:
            about = sections["about"]
            
            # History section
            if "history" in about:
                history = about["history"]
                title = history.get("title", "Tarihçe")
                content = history.get("content", "")
                
                if content:
                    text = f"{faculty_name} - {title}\n\n{content}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "section": "history",
                            "source": source_file
                        }
                    ))
            
            # Vision-Mission section
            if "vision_mission" in about:
                vm = about["vision_mission"]
                
                # Process vision
                if "vision" in vm:
                    vision = vm["vision"]
                    title = vision.get("title", "Vizyon")
                    content = vision.get("content", "")
                    
                    if content:
                        text = f"{faculty_name} - {title}\n\n{content}"
                        doc_hash = compute_hash(text)
                        documents.append(Document(
                            page_content=text,
                            metadata={
                                "hash": doc_hash,
                                "faculty": faculty_name,
                                "section": "vision",
                                "source": source_file
                            }
                        ))
                
                # Process mission
                if "mission" in vm:
                    mission = vm["mission"]
                    title = mission.get("title", "Misyon")
                    content = mission.get("content", "")
                    
                    if content:
                        text = f"{faculty_name} - {title}\n\n{content}"
                        doc_hash = compute_hash(text)
                        documents.append(Document(
                            page_content=text,
                            metadata={
                                "hash": doc_hash,
                                "faculty": faculty_name,
                                "section": "mission",
                                "source": source_file
                            }
                        ))
                
                # Combined vision-mission document
                vision_content = vm.get("vision", {}).get("content", "")
                mission_content = vm.get("mission", {}).get("content", "")
                if vision_content and mission_content:
                    text = f"{faculty_name} - Vizyon ve Misyon\n\nVizyon:\n{vision_content}\n\nMisyon:\n{mission_content}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "section": "vision_mission",
                            "source": source_file
                        }
                    ))
            
            # Quality section
            if "quality" in about:
                quality = about["quality"]
                title = quality.get("title", "Kalite")
                content = quality.get("content", "")
                
                if content:
                    text = f"{faculty_name} - {title}\n\n{content}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "section": "quality",
                            "source": source_file
                        }
                    ))
            
            # Research section
            if "research" in about and about["research"].get("content"):
                research = about["research"]
                title = research.get("title", "Araştırmalar")
                content = research.get("content", "")
                
                if content:
                    text = f"{faculty_name} - {title}\n\n{content}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "section": "research",
                            "source": source_file
                        }
                    ))
            
            # Internationalization section
            if "internationalization" in about and about["internationalization"].get("content"):
                internat = about["internationalization"]
                title = internat.get("title", "Uluslararasılaşma")
                content = internat.get("content", "")
                
                if content:
                    text = f"{faculty_name} - {title}\n\n{content}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "section": "internationalization",
                            "source": source_file
                        }
                    ))
        
        # Management sections
        if "management" in sections:
            management = sections["management"]
            
            # Faculty administration
            if "faculty_administration" in management:
                admin = management["faculty_administration"]
                title = admin.get("title", "Yönetim")
                members = admin.get("members", [])
                
                if members:
                    members_text = "\n".join([f"{m.get('name', '')}: {m.get('title', '')}" for m in members])
                    text = f"{faculty_name} - {title}\n\n{members_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "section": "faculty_administration",
                            "source": source_file
                        }
                    ))
            
            # Faculty management
            if "faculty_management" in management:
                mgmt = management["faculty_management"]
                title = mgmt.get("title", "Fakülte Yönetimi")
                members = mgmt.get("members", [])
                
                if members:
                    members_text = "\n".join([f"{m.get('name', '')}: {m.get('title', '')}" for m in members])
                    text = f"{faculty_name} - {title}\n\n{members_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "section": "faculty_management",
                            "source": source_file
                        }
                    ))
            
            # Faculty board
            if "faculty_board" in management:
                board = management["faculty_board"]
                title = board.get("title", "Fakülte Kurulu")
                members = board.get("members", [])
                
                if members:
                    members_text = "\n".join([f"{m.get('name', '')}: {m.get('title', '')}" for m in members])
                    text = f"{faculty_name} - {title}\n\n{members_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "section": "faculty_board",
                            "source": source_file
                        }
                    ))
            
            # Faculty administrative board
            if "faculty_admin_board" in management:
                admin_board = management["faculty_admin_board"]
                title = admin_board.get("title", "Fakülte Yönetim Kurulu")
                members = admin_board.get("members", [])
                
                if members:
                    members_text = "\n".join([f"{m.get('name', '')}: {m.get('title', '')}" for m in members])
                    text = f"{faculty_name} - {title}\n\n{members_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "section": "faculty_admin_board",
                            "source": source_file
                        }
                    ))
            
            # Department heads
            if "department_heads" in management:
                dept_heads = management["department_heads"]
                title = dept_heads.get("title", "Bölüm Başkanları")
                heads = dept_heads.get("heads", [])
                
                if heads:
                    heads_text = "\n".join([f"{h.get('name', '')}: {h.get('department', '')}" for h in heads])
                    text = f"{faculty_name} - {title}\n\n{heads_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "section": "department_heads",
                            "source": source_file
                        }
                    ))
            
            # Commissions and committees
            if "commissions" in management:
                commissions = management["commissions"]
                title = commissions.get("title", "Komisyon ve Kurullar")
                committees = commissions.get("committees", [])
                
                for committee in committees:
                    committee_name = committee.get("name", "")
                    
                    # Process DUIM members (Maritime Transportation Engineering)
                    if "duim_members" in committee:
                        members = committee["duim_members"]
                        members_text = "\nDeniz Ulaştırma İşletme Mühendisliği Üyeleri:\n"
                        members_text += "\n".join([f"{m.get('name', '')}{': ' + m.get('role', '') if 'role' in m else ''}" for m in members])
                        
                        # Process GMIM members (Marine Engineering)
                        if "gmim_members" in committee:
                            gmim_members = committee["gmim_members"]
                            members_text += "\n\nGemi Makineleri İşletme Mühendisliği Üyeleri:\n"
                            members_text += "\n".join([f"{m.get('name', '')}{': ' + m.get('role', '') if 'role' in m else ''}" for m in gmim_members])
                        
                        text = f"{faculty_name} - {title} - {committee_name}\n\n{members_text}"
                        doc_hash = compute_hash(text)
                        documents.append(Document(
                            page_content=text,
                            metadata={
                                "hash": doc_hash,
                                "faculty": faculty_name,
                                "committee": committee_name,
                                "section": "commissions",
                                "source": source_file
                            }
                        ))
        
        # Academic staff
        if "academic_staff" in sections:
            academic_staff = sections["academic_staff"]
            
            # Maritime Transportation Engineering staff
            if "maritime_transportation_engineering" in academic_staff:
                dept = academic_staff["maritime_transportation_engineering"]
                dept_name = dept.get("name", "Deniz Ulaştırma İşletme Mühendisliği")
                staff = dept.get("staff", [])
                
                if staff:
                    staff_text = "\n".join([f"{s.get('rank', '')} {s.get('name', '')}" for s in staff])
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
            
            # Marine Engineering staff
            if "marine_engineering" in academic_staff:
                dept = academic_staff["marine_engineering"]
                dept_name = dept.get("name", "Gemi Makinaları İşletme Mühendisliği")
                staff = dept.get("staff", [])
                
                if staff:
                    staff_text = "\n".join([f"{s.get('rank', '')} {s.get('name', '')}" for s in staff])
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
        departments = data["departments"]
        
        # Maritime Transportation Engineering
        if "maritime_transportation_engineering" in departments:
            dept = departments["maritime_transportation_engineering"]
            dept_name = dept.get("name", "Deniz Ulaştırma İşletme Mühendisliği")
            
            # Department about section
            if "about" in dept:
                about = dept["about"]
                title = about.get("title", "Bölüm Hakkında")
                content = about.get("content", "")
                
                if content:
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{content}"
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
            if "department_head_message" in dept:
                head_msg = dept["department_head_message"]
                title = head_msg.get("title", "Bölüm Başkanının Mesajı")
                content = head_msg.get("content", "")
                author = head_msg.get("author", "")
                author_title = head_msg.get("title_author", "")
                
                if content:
                    message_text = content
                    if author:
                        message_text += f"\n\n{author}"
                    if author_title:
                        message_text += f"\n{author_title}"
                    
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{message_text}"
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
            
            # Department academic staff
            if "academic_staff" in dept:
                staff = dept["academic_staff"]
                
                if staff:
                    staff_text = ""
                    for s in staff:
                        staff_line = f"{s.get('name', '')}"
                        if "title" in s:
                            staff_line += f": {s.get('title', '')}"
                        if "email" in s:
                            staff_line += f" - {s.get('email', '')}"
                        staff_text += staff_line + "\n"
                    
                    text = f"{faculty_name} - {dept_name} - Akademik Kadro\n\n{staff_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "department": dept_name,
                            "section": "academic_staff_detail",
                            "source": source_file
                        }
                    ))
            
            # Department news
            if "news" in dept:
                news = dept["news"]
                title = news.get("title", "Bölüm Haberleri")
                items = news.get("items", [])
                
                if items:
                    news_text = ""
                    for item in items:
                        news_text += f"• {item.get('title', '')}\n"
                        if "date" in item:
                            news_text += f"  Tarih: {item.get('date', '')}\n"
                        if "source" in item:
                            news_text += f"  Kaynak: {item.get('source', '')}\n"
                        if "link" in item:
                            news_text += f"  Link: {item.get('link', '')}\n"
                        news_text += "\n"
                    
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{news_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "department": dept_name,
                            "section": "news",
                            "source": source_file
                        }
                    ))
            
            # Department events
            if "events" in dept:
                events = dept["events"]
                title = events.get("title", "Bölüm Etkinlikleri")
                items = events.get("items", [])
                
                if items:
                    events_text = ""
                    for item in items:
                        events_text += f"• {item.get('title', '')}\n"
                        if "date" in item:
                            events_text += f"  Tarih: {item.get('date', '')}\n"
                        if "link" in item:
                            events_text += f"  Link: {item.get('link', '')}\n"
                        events_text += "\n"
                    
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{events_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "department": dept_name,
                            "section": "events",
                            "source": source_file
                        }
                    ))
            
            # Department internship
            if "internship" in dept:
                internship = dept["internship"]
                title = internship.get("title", "Staj")
                content = internship.get("content", "")
                
                if content:
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{content}"
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
            
            # Department dual major/minor
            if "dual_major_minor" in dept:
                dual = dept["dual_major_minor"]
                title = dual.get("title", "Çift Yandal/Anadal")
                content = dual.get("content", "")
                
                if content:
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{content}"
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
            
            # Department student clubs
            if "student_clubs" in dept:
                clubs = dept["student_clubs"]
                title = clubs.get("title", "Kulüpler")
                content = clubs.get("content", "")
                
                if content:
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{content}"
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
            
            # Department Erasmus
            if "erasmus" in dept:
                erasmus = dept["erasmus"]
                title = erasmus.get("title", "Erasmus")
                content = erasmus.get("content", "")
                
                if content:
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{content}"
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
            
            # Department graduate
            if "graduate" in dept:
                graduate = dept["graduate"]
                title = graduate.get("title", "Lisansüstü")
                content = graduate.get("content", "")
                
                if content:
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{content}"
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
            
            # Department contact
            if "contact" in dept:
                contact = dept["contact"]
                title = contact.get("title", "İletişim")
                
                contact_text = ""
                if "name" in contact:
                    contact_text += f"Adı: {contact['name']}\n"
                if "department" in contact:
                    contact_text += f"Bölüm: {contact['department']}\n"
                if "campus" in contact:
                    contact_text += f"Kampüs: {contact['campus']}\n"
                if "address" in contact:
                    contact_text += f"Adres: {contact['address']}\n"
                if "phone" in contact:
                    contact_text += f"Telefon: {contact['phone']}\n"
                
                if contact_text:
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{contact_text}"
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
        
        # Marine Engineering
        if "marine_engineering" in departments:
            dept = departments["marine_engineering"]
            dept_name = dept.get("name", "Gemi Makineleri İşletme Mühendisliği")
            
            # Department about section
            if "about" in dept:
                about = dept["about"]
                title = about.get("title", "Bölüm Hakkında")
                content = about.get("content", "")
                
                if content:
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{content}"
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
            if "department_head_message" in dept:
                head_msg = dept["department_head_message"]
                title = head_msg.get("title", "Bölüm Başkanının Mesajı")
                content = head_msg.get("content", "")
                author = head_msg.get("author", "")
                author_title = head_msg.get("title_author", "")
                
                if content:
                    message_text = content
                    if author:
                        message_text += f"\n\n{author}"
                    if author_title:
                        message_text += f"\n{author_title}"
                    
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{message_text}"
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
            
            # Department academic staff
            if "academic_staff" in dept:
                staff = dept["academic_staff"]
                
                if staff:
                    staff_text = ""
                    for s in staff:
                        staff_line = f"{s.get('name', '')}"
                        if "title" in s:
                            staff_line += f": {s.get('title', '')}"
                        if "email" in s:
                            staff_line += f" - {s.get('email', '')}"
                        staff_text += staff_line + "\n"
                    
                    text = f"{faculty_name} - {dept_name} - Akademik Kadro\n\n{staff_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "department": dept_name,
                            "section": "academic_staff_detail",
                            "source": source_file
                        }
                    ))
            
            # Department news
            if "news" in dept:
                news = dept["news"]
                title = news.get("title", "Bölüm Haberleri")
                items = news.get("items", [])
                
                if items:
                    news_text = ""
                    for item in items:
                        news_text += f"• {item.get('title', '')}\n"
                        if "date" in item:
                            news_text += f"  Tarih: {item.get('date', '')}\n"
                        if "source" in item:
                            news_text += f"  Kaynak: {item.get('source', '')}\n"
                        if "link" in item:
                            news_text += f"  Link: {item.get('link', '')}\n"
                        news_text += "\n"
                    
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{news_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "department": dept_name,
                            "section": "news",
                            "source": source_file
                        }
                    ))
            
            # Department news links
            if "news_links" in dept:
                news_links = dept["news_links"]
                title = news_links.get("title", "Haberler")
                items = news_links.get("items", [])
                
                if items:
                    links_text = ""
                    for item in items:
                        links_text += f"• {item.get('title', '')}\n"
                        if "link" in item:
                            links_text += f"  Link: {item.get('link', '')}\n"
                        links_text += "\n"
                    
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{links_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "department": dept_name,
                            "section": "news_links",
                            "source": source_file
                        }
                    ))
            
            # Department events
            if "events" in dept:
                events = dept["events"]
                title = events.get("title", "Bölüm Etkinlikleri")
                items = events.get("items", [])
                
                if items:
                    events_text = ""
                    for item in items:
                        events_text += f"• {item.get('title', '')}\n"
                        if "date" in item:
                            events_text += f"  Tarih: {item.get('date', '')}\n"
                        if "link" in item:
                            events_text += f"  Link: {item.get('link', '')}\n"
                        events_text += "\n"
                    
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{events_text}"
                    doc_hash = compute_hash(text)
                    documents.append(Document(
                        page_content=text,
                        metadata={
                            "hash": doc_hash,
                            "faculty": faculty_name,
                            "department": dept_name,
                            "section": "events",
                            "source": source_file
                        }
                    ))
            
            # Department internship
            if "internship" in dept:
                internship = dept["internship"]
                title = internship.get("title", "Staj")
                content = internship.get("content", "")
                details = internship.get("internship_details", [])
                
                internship_text = content + "\n\n" if content else ""
                
                # Process detailed internship info
                if details:
                    for detail in details:
                        internship_text += f"• {detail.get('name', '')}\n"
                        
                        for key in ["time", "prerequisite", "duration", "location", "additional_info"]:
                            if key in detail:
                                internship_text += f"  {detail[key]}\n"
                        
                        internship_text += "\n"
                
                if internship_text:
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{internship_text}"
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
            
            # Department dual major/minor
            if "dual_major_minor" in dept:
                dual = dept["dual_major_minor"]
                title = dual.get("title", "Çift Yandal/Anadal")
                
                dual_text = ""
                
                # Process quotas
                if "quotas" in dual:
                    quotas = dual["quotas"]
                    dual_text += f"{quotas.get('title', 'KONTENJAN')}\n"
                    dual_text += f"Bölüm: {quotas.get('department', '')}\n"
                    dual_text += f"Çift Anadal: {quotas.get('dual_major', '')}\n"
                    dual_text += f"Yandal: {quotas.get('minor', '')}\n\n"
                
                # Process available programs
                if "programs" in dual:
                    programs = dual["programs"]
                    dual_text += "Programlar:\n"
                    
                    for program in programs:
                        dual_text += f"• {program.get('faculty', '')} - {program.get('department', '')}\n"
                        dual_text += f"  Hedef: {program.get('target_faculty', '')} - {program.get('target_department', '')}\n"
                        dual_text += f"  Çift Anadal: {program.get('dual_major', '')}\n"
                        dual_text += f"  Yandal: {program.get('minor', '')}\n\n"
                
                if dual_text:
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{dual_text}"
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
            
            # Department student clubs
            if "student_clubs" in dept:
                clubs = dept["student_clubs"]
                title = clubs.get("title", "Kulüpler")
                content = clubs.get("content", "")
                link = clubs.get("link", "")
                
                clubs_text = content
                if link:
                    clubs_text += f"\n\nLink: {link}"
                
                if clubs_text:
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{clubs_text}"
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
            
            # Department Erasmus
            if "erasmus" in dept:
                erasmus = dept["erasmus"]
                title = erasmus.get("title", "Erasmus")
                content = erasmus.get("content", "")
                link = erasmus.get("link", "")
                
                erasmus_text = content
                if link:
                    erasmus_text += f"\n\nLink: {link}"
                
                if erasmus_text:
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{erasmus_text}"
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
            
            # Department graduate
            if "graduate" in dept:
                graduate = dept["graduate"]
                title = graduate.get("title", "Lisansüstü")
                content = graduate.get("content", "")
                link = graduate.get("link", "")
                
                graduate_text = content
                if link:
                    graduate_text += f"\n\nLink: {link}"
                
                if graduate_text:
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{graduate_text}"
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
            
            # Department contact
            if "contact" in dept:
                contact = dept["contact"]
                title = contact.get("title", "İletişim")
                
                contact_text = ""
                if "name" in contact:
                    contact_text += f"Adı: {contact['name']}\n"
                if "department" in contact:
                    contact_text += f"Bölüm: {contact['department']}\n"
                if "campus" in contact:
                    contact_text += f"Kampüs: {contact['campus']}\n"
                if "address" in contact:
                    contact_text += f"Adres: {contact['address']}\n"
                if "phone" in contact:
                    contact_text += f"Telefon: {contact['phone']}\n"
                
                if contact_text:
                    text = f"{faculty_name} - {dept_name} - {title}\n\n{contact_text}"
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
    
    return documents