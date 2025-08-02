from langchain.schema import Document
import hashlib
from typing import List, Dict, Any
import json
from datetime import datetime

def compute_hash(content: str) -> str:
    """
    Computes a SHA256 hash from content to prevent duplicate document loading.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Piri Reis Üniversitesi Proje Ofisi Koordinatörlüğü JSON verisini işleyerek 
    LangChain Document nesnelerine dönüştürür.
    
    Args:
        data: Yüklenen JSON verisi (proje_ofisi_koordinatorlugu.json).
        source_file: Kaynak dosya adı.
        
    Returns:
        Document nesnelerinden oluşan bir liste.
    """
    documents = []
    
    # Temel bilgiler
    current_date = data.get("current_date", "")
    
    # Genel bilgiler dokümanı
    general_info = f"Piri Reis Üniversitesi Proje Ofisi Koordinatörlüğü\n\n"
    general_info += f"Güncelleme Tarihi: {current_date}\n\n"
    general_info += f"Hakkımızda: {data.get('hakkimizda', '')}\n\n"
    
    # İletişim bilgileri ekleme
    if "iletisim" in data:
        iletisim = data["iletisim"]
        general_info += "İLETİŞİM BİLGİLERİ\n"
        general_info += f"Adres: {iletisim.get('adres', '')}\n"
        general_info += f"Ofis: {iletisim.get('ofis', '')}\n"
        general_info += f"Dahili Numara: {iletisim.get('dahili_numara', '')}\n"
        general_info += f"E-posta: {iletisim.get('email', '')}\n\n"
    
    # Genel bilgiler dokümanını ekleme
    documents.append(
        Document(
            page_content=general_info,
            metadata={
                "source": source_file,
                "section": "genel_bilgiler",
                "hash": compute_hash(general_info),
                "created_at": datetime.now().isoformat(),
            }
        )
    )
    
    # Ekip bilgileri dokümanı
    if "ekip" in data:
        ekip_content = "PROJE OFİSİ KOORDİNATÖRLÜĞÜ EKİBİ\n\n"
        
        for uye in data["ekip"]:
            ekip_content += f"Ad Soyad: {uye.get('ad_soyad', '')}\n"
            ekip_content += f"Ünvan: {uye.get('unvan', '')}\n"
            ekip_content += f"E-posta: {uye.get('email', '')}\n"
            ekip_content += f"Telefon: {uye.get('telefon', '')}\n\n"
        
        documents.append(
            Document(
                page_content=ekip_content,
                metadata={
                    "source": source_file,
                    "section": "ekip",
                    "hash": compute_hash(ekip_content),
                    "created_at": datetime.now().isoformat(),
                }
            )
        )
    
    # Öğrenciler bölümü
    if "ogrenciler" in data:
        ogrenci_content = "ÖĞRENCİLER İÇİN BİLGİLER\n\n"
        ogrenci_content += f"{data['ogrenciler'].get('aciklama', '')}\n\n"
        ogrenci_content += "DESTEK PROGRAMLARI:\n\n"
        
        for program in data['ogrenciler'].get('destek_programlari', []):
            ogrenci_content += f"Kurum: {program.get('kurum', '')}\n"
            ogrenci_content += f"Başlık: {program.get('baslik', '')}\n"
            ogrenci_content += f"URL: {program.get('url', '')}\n\n"
        
        documents.append(
            Document(
                page_content=ogrenci_content,
                metadata={
                    "source": source_file,
                    "section": "ogrenciler",
                    "hash": compute_hash(ogrenci_content),
                    "created_at": datetime.now().isoformat(),
                }
            )
        )
    
    # Araştırmacılar bölümü
    if "arastirmacilar" in data:
        arastirmacilar_content = "ARAŞTIRMACILAR İÇİN BİLGİLER\n\n"
        arastirmacilar_content += f"Açıklama: {data['arastirmacilar'].get('aciklama', '')}\n\n"
        arastirmacilar_content += f"Satın Alma Süreci: {data['arastirmacilar'].get('satin_alma_sureci', '')}\n\n"
        arastirmacilar_content += f"Tavsiyeler: {data['arastirmacilar'].get('tavsiyeler', '')}\n\n"
        arastirmacilar_content += "FON KAYNAKLARI:\n\n"
        
        for kaynak in data['arastirmacilar'].get('fon_kaynaklari', []):
            arastirmacilar_content += f"Kurum: {kaynak.get('kurum', '')}\n"
            arastirmacilar_content += f"Başlık: {kaynak.get('baslik', '')}\n"
            arastirmacilar_content += f"URL: {kaynak.get('url', '')}\n\n"
        
        documents.append(
            Document(
                page_content=arastirmacilar_content,
                metadata={
                    "source": source_file,
                    "section": "arastirmacilar",
                    "hash": compute_hash(arastirmacilar_content),
                    "created_at": datetime.now().isoformat(),
                }
            )
        )
    
    # Birimler bölümü
    if "birimler" in data:
        # Proje Yönetimi Birimi
        if "proje_yonetimi_birimi" in data["birimler"]:
            proje_yonetimi_content = "PROJE YÖNETİMİ BİRİMİ\n\n"
            proje_yonetimi_content += "GÖREVLER:\n\n"
            
            for gorev in data["birimler"]["proje_yonetimi_birimi"].get("gorevler", []):
                proje_yonetimi_content += f"- {gorev}\n"
            
            documents.append(
                Document(
                    page_content=proje_yonetimi_content,
                    metadata={
                        "source": source_file,
                        "section": "birimler_proje_yonetimi",
                        "hash": compute_hash(proje_yonetimi_content),
                        "created_at": datetime.now().isoformat(),
                    }
                )
            )
        
        # Ticarileştirme ve Girişimcilik Birimi
        if "ticarilestirme_ve_girisimcilik_birimi" in data["birimler"]:
            ticarilestirme_content = "TİCARİLEŞTİRME VE GİRİŞİMCİLİK BİRİMİ\n\n"
            ticarilestirme_content += "GÖREVLER:\n\n"
            
            for gorev in data["birimler"]["ticarilestirme_ve_girisimcilik_birimi"].get("gorevler", []):
                ticarilestirme_content += f"- {gorev}\n"
            
            documents.append(
                Document(
                    page_content=ticarilestirme_content,
                    metadata={
                        "source": source_file,
                        "section": "birimler_ticarilestirme",
                        "hash": compute_hash(ticarilestirme_content),
                        "created_at": datetime.now().isoformat(),
                    }
                )
            )
    
    return documents