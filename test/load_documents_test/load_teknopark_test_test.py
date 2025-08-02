import json
import hashlib
from typing import List, Dict, Any
from langchain.schema import Document

def process_data(data: dict, source_name: str):
    """
    teknopark.json dosyasını işleyerek Langchain Document nesnelerine dönüştüren fonksiyon.
    
    Parameters:
    -----------
    file_path : str
        İşlenecek JSON dosyasının yolu
    source_name : str, optional
        Document nesnesinin metadata'sında yer alacak kaynak adı
        
    Returns:
    --------
    List[Document]
        Oluşturulan Document nesnelerinin listesi
    """
    # Dosyadan JSON verilerini oku
    
    documents = []
    
    # 1. Ana bilgiler ve hedefler için Document
    goals_text = f"# {data['title']}\n\n## Hedefler\n\n"
    goals_text += "\n".join([f"- {goal}" for goal in data['goals']])
    
    goals_doc = Document(
        page_content=goals_text,
        metadata={
            "source": source_name,
            "section": "goals",
            "title": data['title'],
            "created_at": data.get('metadata', {}).get('created_at', ""),
            "created_by": data.get('metadata', {}).get('created_by', ""),
            "hash": hashlib.sha256(goals_text.encode('utf-8')).hexdigest()
        }
    )
    documents.append(goals_doc)
    
    # 2. Çalışma alanları için Document
    if 'research_areas' in data and 'areas' in data['research_areas']:
        areas_title = data['research_areas'].get('title', "Çalışma Alanları")
        areas_text = f"# {data['title']}\n\n## {areas_title}\n\n"
        areas_text += "\n".join([f"- {area}" for area in data['research_areas']['areas']])
        
        areas_doc = Document(
            page_content=areas_text,
            metadata={
                "source": source_name,
                "section": "research_areas",
                "title": f"{data['title']} - {areas_title}",
                "created_at": data.get('metadata', {}).get('created_at', ""),
                "created_by": data.get('metadata', {}).get('created_by', ""),
                "hash": hashlib.sha256(areas_text.encode('utf-8')).hexdigest()
            }
        )
        documents.append(areas_doc)
    
    # 3. Her bir önemli bağlantı için ayrı Document
    if 'important_links' in data and 'links' in data['important_links']:
        links_title = data['important_links'].get('title', "Önemli Bağlantılar")
        
        for link in data['important_links']['links']:
            link_name = link.get('name', "")
            link_url = link.get('url', "")
            
            link_text = f"# {data['title']}\n\n## {links_title}\n\n"
            link_text += f"### {link_name}\n"
            link_text += f"URL: {link_url}"
            
            link_doc = Document(
                page_content=link_text,
                metadata={
                    "source": source_name,
                    "section": "important_links",
                    "subsection": "link",
                    "title": link_name,
                    "url": link_url,
                    "created_at": data.get('metadata', {}).get('created_at', ""),
                    "created_by": data.get('metadata', {}).get('created_by', ""),
                    "hash": hashlib.sha256(link_text.encode('utf-8')).hexdigest()
                }
            )
            documents.append(link_doc)
    
    # 4. Tüm içeriği birleştiren genel bir Document
    all_content = f"# {data['title']}\n\n"
    
    # Hedefler
    all_content += "## Hedefler\n\n"
    all_content += "\n".join([f"- {goal}" for goal in data['goals']])
    all_content += "\n\n"
    
    # Çalışma alanları
    if 'research_areas' in data and 'areas' in data['research_areas']:
        areas_title = data['research_areas'].get('title', "Çalışma Alanları")
        all_content += f"## {areas_title}\n\n"
        all_content += "\n".join([f"- {area}" for area in data['research_areas']['areas']])
        all_content += "\n\n"
    
    # Önemli bağlantılar
    if 'important_links' in data and 'links' in data['important_links']:
        links_title = data['important_links'].get('title', "Önemli Bağlantılar")
        all_content += f"## {links_title}\n\n"
        for link in data['important_links']['links']:
            link_name = link.get('name', "")
            link_url = link.get('url', "")
            all_content += f"- {link_name}: {link_url}\n"
    
    complete_doc = Document(
        page_content=all_content,
        metadata={
            "source": source_name,
            "section": "complete",
            "title": data['title'],
            "created_at": data.get('metadata', {}).get('created_at', ""),
            "created_by": data.get('metadata', {}).get('created_by', ""),
            "hash": hashlib.sha256(all_content.encode('utf-8')).hexdigest()
        }
    )
    documents.append(complete_doc)
    
    return documents