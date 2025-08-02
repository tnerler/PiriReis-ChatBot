from langchain.schema import Document
import hashlib
from typing import List
from datetime import datetime

def compute_hash(content: str) -> str:
    """İçeriğin benzersiz hash değerini hesaplar."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Öğrenci bilgileri JSON verisini işleyerek Document nesneleri oluşturur.
    
    Parameters:
    -----------
    data : dict
        İşlenecek JSON verisi
    source_file : str
        Kaynak dosya yolu
        
    Returns:
    --------
    List[Document]
        Oluşturulan Document nesneleri listesi
    """
    documents = []
    current_date = "2025-07-29 10:59:15"
    user_login = "tnerler"
    
    # Temel bilgileri al
    title = data.get("title", "Öğrenciler için Genel Bilgi")
    sections = data.get("sections", [])
    metadata = data.get("metadata", {})
    
    # Ana doküman içeriği oluştur
    full_content = f"# {title}\n\n"
    full_content += "Bu belge, Piri Reis Üniversitesi öğrencileri için genel bilgiler içermektedir.\n\n"
    
    # Her bölüm için
    for section in sections:
        section_title = section.get("title", "")
        
        # Ana dokümana bölüm başlığı ekle
        full_content += f"## {section_title}\n\n"
        
        # Basit içerik varsa ekle
        if "content" in section:
            full_content += f"{section['content']}\n\n"
            
        # Her bölüm için ayrıntılı içerik oluştur
        section_content = f"# {section_title}\n\n"
        
        # Basit içerik varsa ekle
        if "content" in section:
            section_content += f"{section['content']}\n\n"
        
        # Alt bölümler varsa ekle
        if "subsections" in section:
            for subsection in section.get("subsections", []):
                subsection_title = subsection.get("title", "")
                full_content += f"### {subsection_title}\n\n"
                section_content += f"## {subsection_title}\n\n"
                
                # Alt bölüm içeriği
                if "content" in subsection:
                    full_content += f"{subsection['content']}\n\n"
                    section_content += f"{subsection['content']}\n\n"
                
                # Yurtlar listesi
                if "yurtlar" in subsection:
                    yurtlar = subsection.get("yurtlar", [])
                    full_content += "#### Yurt Listesi\n\n"
                    section_content += "### Yurt Listesi\n\n"
                    
                    for yurt in yurtlar:
                        yurt_info = f"- **{yurt.get('name', '')}**\n"
                        yurt_info += f"  - İlçe: {yurt.get('district', '')}\n"
                        yurt_info += f"  - Adres: {yurt.get('address', '')}\n"
                        if yurt.get("phone"):
                            yurt_info += f"  - Telefon: {yurt.get('phone', '')}\n"
                        yurt_info += "\n"
                        
                        full_content += yurt_info
                        section_content += yurt_info
                
                # Personel listesi
                if "staff" in subsection:
                    staff = subsection.get("staff", [])
                    full_content += "#### Personel Listesi\n\n"
                    section_content += "### Personel Listesi\n\n"
                    
                    for person in staff:
                        person_info = f"- **{person.get('name', '')}**\n"
                        person_info += f"  - Pozisyon: {person.get('position', '')}\n"
                        person_info += f"  - E-posta: {person.get('email', '')}\n"
                        person_info += f"  - Telefon: {person.get('phone', '')}\n"
                        person_info += "\n"
                        
                        full_content += person_info
                        section_content += person_info
                
                # Dokümanlar
                if "documents" in subsection:
                    documents_list = subsection.get("documents", [])
                    full_content += "#### Belgeler\n\n"
                    section_content += "### Belgeler\n\n"
                    
                    for doc in documents_list:
                        if isinstance(doc, dict):
                            doc_info = f"- [{doc.get('name', '')}]({doc.get('url', '')})\n"
                        else:
                            doc_info = f"- {doc}\n"
                        
                        full_content += doc_info
                        section_content += doc_info
                    
                    full_content += "\n"
                    section_content += "\n"
                
                # Gerekli belgeler
                if "required_documents" in subsection:
                    required_docs = subsection.get("required_documents", [])
                    full_content += "#### Gerekli Belgeler\n\n"
                    section_content += "### Gerekli Belgeler\n\n"
                    
                    for doc in required_docs:
                        full_content += f"- {doc}\n"
                        section_content += f"- {doc}\n"
                    
                    full_content += "\n"
                    section_content += "\n"
                
                # Not
                if "note" in subsection:
                    note = subsection.get("note", "")
                    full_content += f"**Not:** {note}\n\n"
                    section_content += f"**Not:** {note}\n\n"
                
                # URL
                if "url" in subsection:
                    url = subsection.get("url", "")
                    full_content += f"[Daha fazla bilgi için tıklayınız]({url})\n\n"
                    section_content += f"[Daha fazla bilgi için tıklayınız]({url})\n\n"
                
                # Staj defterleri kategorileri
                for category_key, display_name in [
                    ("dmyo_mezunlari_staj_defterleri", "DMYO Mezunları Staj Defterleri"),
                    ("dmyo_ogrencileri_staj_defterleri", "DMYO Öğrencileri Staj Defterleri"),
                    ("iktisadi_idari_bilimler_fakultesi_staj_defterleri", "İİBF Staj Defterleri"),
                    ("muhendislik_fakultesi_staj_defterleri", "Mühendislik Fakültesi Staj Defterleri"),
                    ("denizcilik_fakultesi_staj_defterleri", "Denizcilik Fakültesi Staj Defterleri")
                ]:
                    if category_key in subsection:
                        category_docs = subsection.get(category_key, [])
                        full_content += f"#### {display_name}\n\n"
                        section_content += f"### {display_name}\n\n"
                        
                        for doc in category_docs:
                            doc_info = f"- [{doc.get('name', '')}]({doc.get('url', '')})\n"
                            full_content += doc_info
                            section_content += doc_info
                        
                        full_content += "\n"
                        section_content += "\n"
        
        # Kulüpler listesi
        if "clubs" in section:
            clubs = section.get("clubs", [])
            full_content += "### Öğrenci Kulüpleri\n\n"
            section_content += "## Öğrenci Kulüpleri\n\n"
            
            for club in clubs:
                club_info = f"- [{club.get('name', '')}]({club.get('instagram', '')})\n"
                full_content += club_info
                section_content += club_info
            
            full_content += "\n"
            section_content += "\n"
        
        # İletişim bilgileri
        if "contacts" in section:
            contacts = section.get("contacts", [])
            full_content += "### Faydalı İletişim Bilgileri\n\n"
            section_content += "## Faydalı İletişim Bilgileri\n\n"
            
            for contact in contacts:
                contact_info = f"- **{contact.get('name', '')}**: {contact.get('phone', '')}\n"
                full_content += contact_info
                section_content += contact_info
            
            full_content += "\n"
            section_content += "\n"
        
        # Başvuru bilgileri
        if "application_info" in section:
            app_info = section.get("application_info", {})
            app_title = app_info.get("title", "Başvuru Bilgileri")
            
            full_content += f"### {app_title}\n\n"
            section_content += f"## {app_title}\n\n"
            
            # Başvuru maddeleri
            for point in app_info.get("points", []):
                full_content += f"{point}\n\n"
                section_content += f"{point}\n\n"
            
            # İletişim kişileri
            if "contacts" in app_info:
                full_content += "#### İletişim\n\n"
                section_content += "### İletişim\n\n"
                
                for contact in app_info.get("contacts", []):
                    contact_info = f"- **{contact.get('name', '')}**\n"
                    contact_info += f"  - E-posta: {contact.get('email', '')}\n"
                    contact_info += f"  - Telefon: {contact.get('phone', '')}\n\n"
                    
                    full_content += contact_info
                    section_content += contact_info
        
        # Altbilgi
        if "footer" in section:
            footer = section.get("footer", "")
            full_content += f"---\n\n{footer}\n\n"
            section_content += f"---\n\n{footer}\n\n"
        
        # Her bölüm için bir doküman oluştur
        section_hash = compute_hash(section_content)
        documents.append(Document(
            page_content=section_content,
            metadata={
                "hash": section_hash,
                "title": f"{title} - {section_title}",
                "section": section_title,
                "source": source_file,
                "document_type": "ogrenci_bilgi_bolum",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Bazı önemli konular için özel dokümanlar oluştur
    
    # Staj Rehberi
    staj_section = next((section for section in sections if section.get("title") == "STAJ"), None)
    if staj_section:
        staj_content = "# Staj Rehberi\n\n"
        staj_content += "Bu belge, Piri Reis Üniversitesi öğrencileri için staj süreciyle ilgili bilgileri içermektedir.\n\n"
        
        # Ofis bilgisi
        office_subsection = next((sub for sub in staj_section.get("subsections", []) if sub.get("title") == "KURUMSAL STAJ OFİSİ"), None)
        if office_subsection and "staff" in office_subsection:
            staj_content += "## Staj Ofisi İletişim Bilgileri\n\n"
            
            for person in office_subsection.get("staff", []):
                staj_content += f"- **{person.get('name', '')}** ({person.get('position', '')})\n"
                staj_content += f"  - E-posta: {person.get('email', '')}\n"
                staj_content += f"  - Telefon: {person.get('phone', '')}\n\n"
        
        # Başvuru bilgileri
        docs_subsection = next((sub for sub in staj_section.get("subsections", []) if "Staj Başvuru Evrakları" in sub.get("title", "")), None)
        if docs_subsection:
            staj_content += "## Başvuru Sürecinde Gerekli Belgeler\n\n"
            staj_content += docs_subsection.get("content", "") + "\n\n"
            
            if "documents" in docs_subsection:
                for doc in docs_subsection.get("documents", []):
                    if isinstance(doc, dict):
                        staj_content += f"- [{doc.get('name', '')}]({doc.get('url', '')})\n"
        
        # Fakültelere göre staj defterleri
        defter_subsection = next((sub for sub in staj_section.get("subsections", []) if sub.get("title") == "STAJ DEFTERLERİ"), None)
        if defter_subsection:
            staj_content += "## Fakülte ve Bölümlere Göre Staj Defterleri\n\n"
            
            # Her fakülte için ayrı başlık
            for category_key, display_name in [
                ("denizcilik_fakultesi_staj_defterleri", "Denizcilik Fakültesi"),
                ("muhendislik_fakultesi_staj_defterleri", "Mühendislik Fakültesi"),
                ("iktisadi_idari_bilimler_fakultesi_staj_defterleri", "İktisadi ve İdari Bilimler Fakültesi"),
                ("dmyo_ogrencileri_staj_defterleri", "Denizcilik Meslek Yüksekokulu Öğrencileri"),
                ("dmyo_mezunlari_staj_defterleri", "Denizcilik Meslek Yüksekokulu Mezunları")
            ]:
                if category_key in defter_subsection:
                    staj_content += f"### {display_name}\n\n"
                    
                    for doc in defter_subsection.get(category_key, []):
                        staj_content += f"- [{doc.get('name', '')}]({doc.get('url', '')})\n"
                    
                    staj_content += "\n"
        
        # Staj dokümanı oluştur
        staj_hash = compute_hash(staj_content)
        documents.append(Document(
            page_content=staj_content,
            metadata={
                "hash": staj_hash,
                "title": "Staj Rehberi",
                "source": source_file,
                "document_type": "ogrenci_rehber",
                "category": "staj",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Barınma Rehberi
    barinma_section = next((section for section in sections if section.get("title") == "Barınma"), None)
    if barinma_section:
        barinma_content = "# Barınma Rehberi\n\n"
        barinma_content += "Bu belge, Piri Reis Üniversitesi öğrencileri için barınma seçenekleri hakkında bilgiler içermektedir.\n\n"
        
        # Yurt bilgileri
        for subsection in barinma_section.get("subsections", []):
            barinma_content += f"## {subsection.get('title', '')}\n\n"
            
            if "content" in subsection:
                barinma_content += f"{subsection.get('content')}\n\n"
            
            if "yurtlar" in subsection:
                # İlçelere göre grupla
                districts = {}
                for yurt in subsection.get("yurtlar", []):
                    district = yurt.get("district", "Diğer")
                    if district not in districts:
                        districts[district] = []
                    districts[district].append(yurt)
                
                # Her ilçe için yurtları listele
                for district, yurtlar in sorted(districts.items()):
                    barinma_content += f"### {district} İlçesindeki Yurtlar\n\n"
                    
                    for yurt in yurtlar:
                        barinma_content += f"- **{yurt.get('name', '')}**\n"
                        barinma_content += f"  - Adres: {yurt.get('address', '')}\n"
                        if yurt.get("phone"):
                            barinma_content += f"  - Telefon: {yurt.get('phone', '')}\n"
                        barinma_content += "\n"
        
        # Barınma tavsiye ve ipuçları
        barinma_content += "## Barınma Tavsiye ve İpuçları\n\n"
        barinma_content += "1. Yurt başvuruları için KYK veya özel yurt web sitelerini düzenli olarak kontrol edin\n"
        barinma_content += "2. Erken başvuru yapmak kontenjan dolmadan yer bulmanıza yardımcı olacaktır\n"
        barinma_content += "3. İnternet ve ulaşım olanaklarını mutlaka değerlendirin\n"
        barinma_content += "4. Yurt seçiminde güvenliğe önem verin\n"
        barinma_content += "5. Farklı seçenekleri karşılaştırın ve bütçenize uygun olanı tercih edin\n\n"
        
        barinma_content += "Detaylı bilgi için Öğrenci Dekanlığı ile iletişime geçebilirsiniz.\n"
        
        # Barınma dokümanı oluştur
        barinma_hash = compute_hash(barinma_content)
        documents.append(Document(
            page_content=barinma_content,
            metadata={
                "hash": barinma_hash,
                "title": "Öğrenci Barınma Rehberi",
                "source": source_file,
                "document_type": "ogrenci_rehber",
                "category": "barınma",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Sosyal İmkanlar Rehberi
    sosyal_section = next((section for section in sections if section.get("title") == "Spor ve Sosyal Yaşam" or section.get("title") == "Piri Reis Üniversitesi'nde Spor"), None)
    kulup_section = next((section for section in sections if section.get("title") == "Öğrenci Kulüpleri"), None)
    
    if sosyal_section or kulup_section:
        sosyal_content = "# Sosyal İmkanlar Rehberi\n\n"
        sosyal_content += "Bu belge, Piri Reis Üniversitesi'nde öğrencilere sunulan sosyal ve sportif imkanlar hakkında bilgiler içermektedir.\n\n"
        
        # Spor imkanları
        if sosyal_section:
            sosyal_content += "## Spor İmkanları\n\n"
            
            if "content" in sosyal_section:
                sosyal_content += f"{sosyal_section.get('content')}\n\n"
            
            # Spor personeli
            if "subsections" in sosyal_section:
                for subsection in sosyal_section.get("subsections", []):
                    if "staff" in subsection:
                        sosyal_content += "## Spor ve Sosyal Hizmetler Personeli\n\n"
                        
                        for person in subsection.get("staff", []):
                            sosyal_content += f"- **{person.get('name', '')}** ({person.get('position', '')})\n"
                            sosyal_content += f"  - E-posta: {person.get('email', '')}\n"
                            sosyal_content += f"  - Telefon: {person.get('phone', '')}\n\n"
        
        # Öğrenci kulüpleri
        if kulup_section and "clubs" in kulup_section:
            sosyal_content += "## Öğrenci Kulüpleri\n\n"
            
            # Kategorilere göre grupla
            categories = {
                "denizcilik": [],
                "spor": [],
                "sanat_kultur": [],
                "akademik": [],
                "sosyal": []
            }
            
            for club in kulup_section.get("clubs", []):
                name = club.get("name", "").lower()
                
                if "deniz" in name or "broker" in name or "yacht" in name or "yat" in name:
                    categories["denizcilik"].append(club)
                elif "spor" in name or "fitness" in name or "dalış" in name or "dans" in name:
                    categories["spor"].append(club)
                elif "sanat" in name or "müzik" in name or "felsefe" in name:
                    categories["sanat_kultur"].append(club)
                elif "mühendislik" in name or "bilişim" in name or "robot" in name or "tech" in name:
                    categories["akademik"].append(club)
                else:
                    categories["sosyal"].append(club)
            
            # Her kategori için kulüpleri listele
            for category_key, display_name in [
                ("denizcilik", "Denizcilik Kulüpleri"),
                ("spor", "Spor Kulüpleri"),
                ("sanat_kultur", "Sanat ve Kültür Kulüpleri"),
                ("akademik", "Akademik Kulüpler"),
                ("sosyal", "Sosyal ve Diğer Kulüpler")
            ]:
                if categories[category_key]:
                    sosyal_content += f"### {display_name}\n\n"
                    
                    for club in categories[category_key]:
                        sosyal_content += f"- [{club.get('name', '')}]({club.get('instagram', '')})\n"
                    
                    sosyal_content += "\n"
        
        # Etkinlik ve organizasyonlar
        sosyal_content += "## Etkinlikler ve Organizasyonlar\n\n"
        sosyal_content += "Piri Reis Üniversitesi'nde yıl boyunca çeşitli etkinlikler düzenlenmektedir:\n\n"
        sosyal_content += "- Bahar Şenlikleri\n"
        sosyal_content += "- Kulüp Tanıtım Günleri\n"
        sosyal_content += "- Denizcilik Seminerleri\n"
        sosyal_content += "- Kariyer Günleri\n"
        sosyal_content += "- Sportif Turnuvalar\n"
        sosyal_content += "- Yelken ve Deniz Sporları Etkinlikleri\n\n"
        
        sosyal_content += "Etkinliklerden haberdar olmak için üniversite web sitesini takip edebilir veya öğrenci kulüplerinin sosyal medya hesaplarını inceleyebilirsiniz.\n"
        
        # Sosyal imkanlar dokümanı oluştur
        sosyal_hash = compute_hash(sosyal_content)
        documents.append(Document(
            page_content=sosyal_content,
            metadata={
                "hash": sosyal_hash,
                "title": "Sosyal ve Sportif İmkanlar Rehberi",
                "source": source_file,
                "document_type": "ogrenci_rehber",
                "category": "sosyal",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Sağlık Hizmetleri Rehberi
    saglik_section = next((section for section in sections if section.get("title") == "SAĞLIK HİZMETLERİ" or section.get("title") == "Sağlık Hizmetleri Birimi"), None)
    sigorta_section = next((section for section in sections if section.get("title") == "SİGORTA"), None)
    
    if saglik_section or sigorta_section:
        saglik_content = "# Öğrenci Sağlık Hizmetleri Rehberi\n\n"
        saglik_content += "Bu belge, Piri Reis Üniversitesi öğrencileri için sağlık hizmetleri ve sigortayla ilgili bilgileri içermektedir.\n\n"
        
        # Sağlık hizmetleri
        if saglik_section:
            saglik_content += "## Üniversite Sağlık Hizmetleri\n\n"
            
            if "content" in saglik_section:
                saglik_content += f"{saglik_section.get('content')}\n\n"
        
        # Sigorta bilgileri
        if sigorta_section:
            saglik_content += "## Sigorta Bilgileri\n\n"
            
            if "content" in sigorta_section:
                saglik_content += f"{sigorta_section.get('content')}\n\n"
        
        # Acil durumlar
        saglik_content += "## Acil Durumlarda Yapılması Gerekenler\n\n"
        saglik_content += "1. Acil bir sağlık sorunu yaşandığında öncelikle Üniversite Sağlık Birimi'ni arayın: 0 (216) 581 00 11\n"
        saglik_content += "2. Sağlık Birimi kapalıysa veya kampüs dışındaysanız 112 Acil Servisi arayın\n"
        saglik_content += "3. Durumu Öğrenci Dekanlığı'na bildirin\n"
        saglik_content += "4. Tedavi sonrası sağlık raporunuzu Öğrenci İşleri'ne iletmeyi unutmayın\n\n"
        
        # Yakın sağlık kurumları
        saglik_content += "## Kampüs Çevresindeki Sağlık Kurumları\n\n"
        saglik_content += "- **Tuzla Devlet Hastanesi**\n"
        saglik_content += "  - Adres: İçmeler, Dr. Ali Menteşe Cd. No:2, 34947 Tuzla/İstanbul\n"
        saglik_content += "  - Telefon: (0216) 395 97 50\n\n"
        saglik_content += "- **Pendik Devlet Hastanesi**\n"
        saglik_content += "  - Adres: Batı, Banu Sk., 34890 Pendik/İstanbul\n"
        saglik_content += "  - Telefon: (0216) 491 56 56\n\n"
        
        # Sağlık dokümanı oluştur
        saglik_hash = compute_hash(saglik_content)
        documents.append(Document(
            page_content=saglik_content,
            metadata={
                "hash": saglik_hash,
                "title": "Öğrenci Sağlık Hizmetleri Rehberi",
                "source": source_file,
                "document_type": "ogrenci_rehber",
                "category": "sağlık",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Ana doküman için özet bilgiler
    full_content += "## Öğrenci Destek Birimleri\n\n"
    full_content += "Üniversitemizdeki öğrenci destek birimleri ve iletişim bilgileri:\n\n"
    full_content += "| Birim | Konum | İletişim |\n"
    full_content += "|-------|-------|----------|\n"
    full_content += "| Öğrenci İşleri | Ana Bina | +90 216 581 0050 |\n"
    full_content += "| Sağlık Birimi | B-Blok 0. Kat | +90 216 581 00 11 |\n"
    full_content += "| Öğrenci Dekanlığı | Ana Bina | +90 216 581 0050 (1354) |\n"
    full_content += "| Kurumsal Staj Ofisi | Ana Bina | +90 216 581 0050 (1454) |\n"
    full_content += "| Psikolojik Danışma | B-Blok Zemin Kat (B-Z12) | +90 216 581 0050 (1789) |\n"
    
    # Ana doküman ekle
    full_hash = compute_hash(full_content)
    documents.append(Document(
        page_content=full_content,
        metadata={
            "hash": full_hash,
            "title": title,
            "source": source_file,
            "document_type": "ogrenci_bilgi_tam",
            "section_count": len(sections),
            "file_name": metadata.get("file_name", source_file.split("/")[-1] if "/" in source_file else source_file),
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    return documents