from langchain.schema import Document
import hashlib
from typing import List
from datetime import datetime


def compute_hash(content: str) -> str:
    """
    İçerik için bir hash değeri hesaplar.
    """
    import hashlib
    return hashlib.md5(content.encode()).hexdigest()

def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Rektör bilgileri JSON verisini işleyerek Document nesneleri oluşturur.
    """
    documents = []
    current_date = "2025-07-31 07:04:37"
    user_login = "tnerler"
    
    university_name = "Piri Reis Üniversitesi"
    rektor_name = f"{data['kisiselBilgiler']['unvan']} {data['kisiselBilgiler']['ad']} {data['kisiselBilgiler']['soyad']}"
    
    # Ana doküman oluştur - Rektör Biyografisi
    bio_content = f"# {university_name} - Rektör Biyografisi\n\n"
    bio_content += f"## {rektor_name}\n\n"
    bio_content += f"**Pozisyon:** {data['kisiselBilgiler']['pozisyon']}\n\n"
    bio_content += f"**Atama Tarihi:** \n- Vekillik: {data['kisiselBilgiler']['atamaTarihi']['vekillik']}\n- Asaleten: {data['kisiselBilgiler']['atamaTarihi']['asaleten']}\n\n"
    
    # Eğitim Bilgileri
    bio_content += "## Eğitim Bilgileri\n\n"
    bio_content += f"**Lisans:** {data['egitimBilgileri']['lisans']['okul']}, {data['egitimBilgileri']['lisans']['bolum']} ({data['egitimBilgileri']['lisans']['yil']})\n\n"
    bio_content += f"**Lisansüstü:** {data['egitimBilgileri']['lisansustu']['okul']}, {data['egitimBilgileri']['lisansustu']['bolum']}\n"
    
    if data['egitimBilgileri']['lisansustu'].get('yuksekLisans', False):
        bio_content += "- Yüksek Lisans\n"
    if data['egitimBilgileri']['lisansustu'].get('doktora', False):
        bio_content += "- Doktora\n"
    bio_content += "\n"
    
    # Doktora Sonrası
    bio_content += "**Doktora Sonrası:**\n"
    for kurum in data['egitimBilgileri']['doktoraSonrasi']['kurumlar']:
        bio_content += f"- {kurum['kurum']}, {kurum['yer']}"
        if 'bolum' in kurum:
            bio_content += f", {kurum['bolum']}"
        if 'yillar' in kurum:
            bio_content += f" ({kurum['yillar']})"
        bio_content += "\n"
    bio_content += "\n"
    
    # Ödüller
    if 'oduller' in data and data['oduller']:
        bio_content += "## Ödüller\n\n"
        for odul in data['oduller']:
            bio_content += f"- {odul['ad']}, {odul['kurum']} ({odul['yil']})\n"
        bio_content += "\n"
    
    # İş Tecrübesi
    bio_content += "## İş Tecrübesi\n\n"
    for is_tecrube in data['isTecrubesi']:
        bio_content += f"### {is_tecrube['kurum']}\n"
        if 'bolum' in is_tecrube:
            bio_content += f"**Bölüm:** {is_tecrube['bolum']}\n"
        
        if 'pozisyon' in is_tecrube:
            if isinstance(is_tecrube['pozisyon'], list):
                bio_content += "**Pozisyonlar:**\n"
                for poz in is_tecrube['pozisyon']:
                    bio_content += f"- {poz}\n"
            else:
                bio_content += f"**Pozisyon:** {is_tecrube['pozisyon']}\n"
        
        if 'pozisyonlar' in is_tecrube:
            bio_content += "**Pozisyonlar:**\n"
            for poz in is_tecrube['pozisyonlar']:
                bio_content += f"- {poz['pozisyon']}"
                if 'yillar' in poz:
                    bio_content += f" ({poz['yillar']})"
                if 'sure' in poz:
                    bio_content += f" ({poz['sure']})"
                bio_content += "\n"
        
        if 'sure' in is_tecrube:
            bio_content += f"**Süre:** {is_tecrube['sure']}\n"
        if 'yillar' in is_tecrube:
            bio_content += f"**Yıllar:** {is_tecrube['yillar']}\n"
        if 'baslangic' in is_tecrube:
            bio_content += "**Başlangıç:**\n"
            for key, value in is_tecrube['baslangic'].items():
                bio_content += f"- {key.capitalize()}: {value}\n"
        
        bio_content += "\n"
    
    # Araştırma Alanları
    bio_content += "## Araştırma Alanları\n\n"
    for alan in data['arastirmaAlanlari']:
        bio_content += f"- {alan}\n"
    bio_content += "\n"
    
    # Üyelikler
    bio_content += "## Üyelikler\n\n"
    for uyelik in data['uyelikler']:
        bio_content += f"- {uyelik}\n"
    bio_content += "\n"
    
    # Sportif Faaliyetler
    if 'sportifFaaliyetler' in data:
        bio_content += "## Sportif Faaliyetler\n\n"
        bio_content += f"**Kulüp:** {data['sportifFaaliyetler']['kulup']}\n"
        bio_content += f"**Branş:** {data['sportifFaaliyetler']['brans']}\n"
        bio_content += f"**Süre:** {data['sportifFaaliyetler']['sure']}\n"
        
        if 'basarilar' in data['sportifFaaliyetler'] and data['sportifFaaliyetler']['basarilar']:
            bio_content += "**Başarılar:**\n"
            for basari in data['sportifFaaliyetler']['basarilar']:
                bio_content += f"- {basari}\n"
        bio_content += "\n"
    
    # Ana biyografi dokümanını ekle
    bio_hash = compute_hash(bio_content)
    documents.append(Document(
        page_content=bio_content,
        metadata={
            "hash": bio_hash,
            "title": f"{university_name} - Rektör Biyografisi",
            "university": university_name,
            "rektor": rektor_name,
            "document_type": "rektor_biyografi",
            "source": source_file,
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    # Rektör Mesajı Dokümanı
    if 'rektorMesaji' in data:
        mesaj_content = f"# {university_name} - Rektör Mesajı\n\n"
        mesaj_content += f"## {rektor_name}\n\n"
        
        mesaj_content += f"### {data['rektorMesaji']['hitap']}\n\n"
        
        for paragraf in data['rektorMesaji']['paragraflar']:
            mesaj_content += f"{paragraf}\n\n"
        
        if 'ogrenciMesaji' in data['rektorMesaji']:
            mesaj_content += f"### {data['rektorMesaji']['ogrenciMesaji']['hitap']}\n\n"
            for paragraf in data['rektorMesaji']['ogrenciMesaji']['paragraflar']:
                mesaj_content += f"{paragraf}\n\n"
        
        mesaj_content += f"{data['rektorMesaji']['kapaniş']}\n\n"
        mesaj_content += f"{data['rektorMesaji']['imza']}"
        
        mesaj_hash = compute_hash(mesaj_content)
        documents.append(Document(
            page_content=mesaj_content,
            metadata={
                "hash": mesaj_hash,
                "title": f"{university_name} - Rektör Mesajı",
                "university": university_name,
                "rektor": rektor_name,
                "document_type": "rektor_mesaj",
                "source": source_file,
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Video bağlantısı varsa ayrı bir doküman olarak ekle
    if 'videoBaglantisi' in data['kisiselBilgiler']:
        video_content = f"# {university_name} - Rektör Videosu\n\n"
        video_content += f"## {rektor_name}\n\n"
        video_content += f"**Rektörün Video Bağlantısı:** [{data['kisiselBilgiler']['videoBaglantisi']}]({data['kisiselBilgiler']['videoBaglantisi']})\n\n"
        
        video_hash = compute_hash(video_content)
        documents.append(Document(
            page_content=video_content,
            metadata={
                "hash": video_hash,
                "title": f"{university_name} - Rektör Videosu",
                "university": university_name,
                "rektor": rektor_name,
                "document_type": "rektor_video",
                "source": source_file,
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    return documents
