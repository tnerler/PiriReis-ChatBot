from langchain.schema import Document
import hashlib
from typing import List, Dict, Any
import json
from datetime import datetime

def compute_hash(content: str) -> str:
    """
    İçeriğin benzersiz bir hash değerini hesaplar.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Piri Reis Üniversitesi kampüs ulaşım bilgileri JSON verisini işleyerek 
    LangChain Document nesnelerine dönüştürür.
    
    Args:
        data: Yüklenen JSON verisi.
        source_file: Kaynak dosya adı.
        
    Returns:
        Document nesnelerinden oluşan bir liste.
    """
    documents = []
    current_date = "2025-07-25 08:18:55"  # UTC format
    user_login = "tnerler"
    
    # Ana bilgileri al
    doc_title = data.get("document_title", "")
    metadata = data.get("metadata", {})
    university_name = metadata.get("university_name", "Piri Reis Üniversitesi")
    
    # Tüm ulaşım bilgilerini içeren ana doküman oluştur
    full_content = f"{doc_title}\n\n"
    
    # Çalışma saatleri bölümü
    working_hours = data.get("working_hours", {})
    if working_hours:
        full_content += "## Çalışma Saatleri\n\n"
        full_content += f"{working_hours.get('days', '')}: {working_hours.get('hours', '')}\n\n"
    
    # Üniversite servis bilgileri
    university_services = data.get("university_services", {})
    if university_services:
        full_content += "## Üniversite Servisleri\n\n"
        shuttles = university_services.get("shuttles", [])
        for shuttle in shuttles:
            location = shuttle.get("location", "")
            time = shuttle.get("time", "")
            notes = shuttle.get("notes", "")
            
            full_content += f"- {location}: {time}"
            if notes:
                full_content += f" ({notes})"
            full_content += "\n"
        full_content += "\n"
    
    # Ulaşım yöntemleri
    transportation_methods = data.get("transportation_methods", [])
    if transportation_methods:
        full_content += "## Ulaşım Bilgileri\n\n"
        
        for method in transportation_methods:
            method_name = method.get("method_name", "")
            description = method.get("description", "")
            
            full_content += f"### {method_name}\n\n"
            full_content += f"{description}\n\n"
            
            # Yönteme göre ek bilgileri ekle
            if method_name == "Otobüs":
                lines = method.get("lines", [])
                if lines:
                    full_content += f"**Otobüs Hatları:** {', '.join(lines)}\n"
                stop_name = method.get("stop_name", "")
                if stop_name:
                    full_content += f"**Durak:** {stop_name}\n"
            
            elif method_name == "Deniz Ulaşımı":
                vessel_types = method.get("vessel_types", [])
                if vessel_types:
                    full_content += f"**Deniz Taşıtları:** {', '.join(vessel_types)}\n"
                port_name = method.get("port_name", "")
                if port_name:
                    full_content += f"**İskele:** {port_name}\n"
            
            elif method_name == "Havalimanından":
                airports = method.get("airports", [])
                for airport in airports:
                    airport_name = airport.get("name", "")
                    duration = airport.get("duration", "")
                    full_content += f"**{airport_name}:** {duration}\n"
            
            full_content += "\n"
    
    # Kampüs konum bilgileri
    campus_location = data.get("campus_location", {})
    if campus_location:
        full_content += "## Kampüs Konumu\n\n"
        neighborhood = campus_location.get("neighborhood", "")
        district = campus_location.get("district", "")
        city = campus_location.get("city", "")
        
        full_content += f"{neighborhood}, {district}, {city}\n\n"
    
    # Kampüs binaları
    campus_buildings = data.get("campus_buildings", {})
    if campus_buildings:
        full_content += "## Kampüs Binaları\n\n"
        for building_code, building_desc in campus_buildings.items():
            full_content += f"**{building_code}:** {building_desc}\n"
        full_content += "\n"
    
    # Tam doküman için bir Document oluştur
    full_hash = compute_hash(full_content)
    documents.append(Document(
        page_content=full_content,
        metadata={
            "hash": full_hash,
            "title": doc_title,
            "university": university_name,
            "source": source_file,
            "document_type": "ulasim_tam",
            "processed_date": current_date,
            "processed_by": user_login,
            "tags": ", ".join(metadata.get("tags", []))
        }
    ))
    
    # Her ulaşım yöntemi için ayrı doküman oluştur
    for method in transportation_methods:
        method_name = method.get("method_name", "")
        description = method.get("description", "")
        
        method_content = f"# {university_name} - {method_name} ile Ulaşım\n\n"
        method_content += f"{description}\n\n"
        
        # Yönteme göre ek bilgileri ekle
        if method_name == "Özel Araç":
            route_instructions = method.get("route_instructions", "")
            duration = method.get("duration", "")
            
            if route_instructions:
                method_content += f"**Rota:** {route_instructions}\n"
            if duration:
                method_content += f"**Süre:** {duration}\n"
            
            # Konum bilgilerini ekle
            if campus_location:
                neighborhood = campus_location.get("neighborhood", "")
                district = campus_location.get("district", "")
                city = campus_location.get("city", "")
                
                method_content += f"\n**Adres:** {neighborhood}, {district}, {city}\n"
        
        elif method_name == "Marmaray":
            stop_name = method.get("stop_name", "")
            duration = method.get("duration", "")
            
            if stop_name:
                method_content += f"**İstasyon:** {stop_name}\n"
            if duration:
                method_content += f"**Yürüme Mesafesi:** {duration}\n"
            
            method_content += "\n**İpucu:** İstasyon çıkışında üniversite yönlendirme tabelalarını takip edebilirsiniz.\n"
        
        elif method_name == "Otobüs":
            lines = method.get("lines", [])
            stop_name = method.get("stop_name", "")
            
            if lines:
                method_content += f"**Otobüs Hatları:** {', '.join(lines)}\n"
            if stop_name:
                method_content += f"**Durak:** {stop_name}\n"
            
            method_content += "\n**Nereden Binebilirsiniz?**\nBu otobüs hatları İstanbul'un çeşitli noktalarından Tuzla'ya ulaşım sağlar.\n"
        
        elif method_name == "Deniz Ulaşımı":
            vessel_types = method.get("vessel_types", [])
            port_name = method.get("port_name", "")
            duration = method.get("duration", "")
            
            if vessel_types:
                method_content += f"**Deniz Taşıtları:** {', '.join(vessel_types)}\n"
            if port_name:
                method_content += f"**İskele:** {port_name}\n"
            if duration:
                method_content += f"**Yürüme Mesafesi:** {duration}\n"
            
            method_content += "\n**İstanbul'dan Deniz Ulaşımı**\nİstanbul'un çeşitli iskelelerinden Tuzla'ya deniz otobüsü ve vapur seferleri bulunmaktadır.\n"
        
        elif method_name == "Havalimanından":
            airports = method.get("airports", [])
            method_content += "**Havalimanlarından Ulaşım**\n\n"
            
            for airport in airports:
                airport_name = airport.get("name", "")
                duration = airport.get("duration", "")
                
                method_content += f"- **{airport_name}:** {duration}\n"
            
            method_content += "\n**Alternatif Ulaşım**\nHavalimanlarından toplu taşıma araçlarıyla da kampüsümüze ulaşabilirsiniz.\n"
        
        # Çalışma saatleri bilgisini ekle
        if working_hours:
            method_content += f"\n## Kampüs Çalışma Saatleri\n\n"
            method_content += f"{working_hours.get('days', '')}: {working_hours.get('hours', '')}\n"
        
        # Metoda göre doküman oluştur
        method_hash = compute_hash(method_content)
        documents.append(Document(
            page_content=method_content,
            metadata={
                "hash": method_hash,
                "title": f"{university_name} - {method_name} ile Ulaşım",
                "university": university_name,
                "transport_method": method_name,
                "source": source_file,
                "document_type": "ulasim_yontem",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Üniversite servisleri için ayrı doküman
    if university_services:
        services_content = f"# {university_name} - Servis Bilgileri\n\n"
        
        services_content += "## Üniversite Servisleri\n\n"
        shuttles = university_services.get("shuttles", [])
        services_content += "| Lokasyon | Saat | Not |\n"
        services_content += "|----------|------|-----|\n"
        
        for shuttle in shuttles:
            location = shuttle.get("location", "")
            time = shuttle.get("time", "")
            notes = shuttle.get("notes", "") or "-"
            
            services_content += f"| {location} | {time} | {notes} |\n"
        
        services_content += "\n**Not:** Servis saatlerinde değişiklik olabilir, güncel bilgi için üniversite ulaşım ofisiyle iletişime geçiniz.\n\n"
        
        # Çalışma saatleri bilgisini ekle
        if working_hours:
            services_content += f"## Kampüs Çalışma Saatleri\n\n"
            services_content += f"{working_hours.get('days', '')}: {working_hours.get('hours', '')}\n"
        
        # Servis dokümanı oluştur
        services_hash = compute_hash(services_content)
        documents.append(Document(
            page_content=services_content,
            metadata={
                "hash": services_hash,
                "title": f"{university_name} - Servis Bilgileri",
                "university": university_name,
                "source": source_file,
                "document_type": "ulasim_servis",
                "processed_date": current_date,
                "processed_by": user_login
            }
        ))
    
    # Kampüs haritası ve konum bilgisi için doküman
    campus_content = f"# {university_name} - Kampüs Konumu ve Bilgileri\n\n"
    
    # Konum bilgilerini ekle
    if campus_location:
        campus_content += "## Kampüs Konumu\n\n"
        neighborhood = campus_location.get("neighborhood", "")
        district = campus_location.get("district", "")
        city = campus_location.get("city", "")
        
        campus_content += f"{university_name} kampüsü {neighborhood}, {district}, {city}'da bulunmaktadır.\n\n"
    
    # Kampüs binaları
    if campus_buildings:
        campus_content += "## Kampüs Binaları\n\n"
        campus_content += "| Bina Kodu | Açıklama |\n"
        campus_content += "|-----------|----------|\n"
        
        for building_code, building_desc in campus_buildings.items():
            campus_content += f"| {building_code} | {building_desc} |\n"
        campus_content += "\n"
    
    # Çalışma saatleri bilgisini ekle
    if working_hours:
        campus_content += f"## Çalışma Saatleri\n\n"
        campus_content += f"{working_hours.get('days', '')}: {working_hours.get('hours', '')}\n\n"
    
    # Ulaşım özeti ekle
    campus_content += "## Ulaşım Özeti\n\n"
    for method in transportation_methods:
        method_name = method.get("method_name", "")
        description_short = method.get("description", "").split(".")[0] + "."
        
        campus_content += f"- **{method_name}:** {description_short}\n"
    
    # Kampüs dokümanı oluştur
    campus_hash = compute_hash(campus_content)
    documents.append(Document(
        page_content=campus_content,
        metadata={
            "hash": campus_hash,
            "title": f"{university_name} - Kampüs Konumu ve Bilgileri",
            "university": university_name,
            "location": f"{campus_location.get('district', '')}, {campus_location.get('city', '')}" if campus_location else "",
            "source": source_file,
            "document_type": "kampus_konum",
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    # Sıkça sorulan sorular formatında bir doküman
    faq_content = f"# {university_name} Ulaşım Sıkça Sorulan Sorular\n\n"
    
    faq_content += "## Piri Reis Üniversitesi'ne nasıl ulaşabilirim?\n\n"
    faq_content += "Piri Reis Üniversitesi'ne çeşitli ulaşım araçlarıyla ulaşabilirsiniz:\n"
    for method in transportation_methods:
        method_name = method.get("method_name", "")
        description_short = method.get("description", "").split(".")[0] + "."
        faq_content += f"- **{method_name}:** {description_short}\n"
    faq_content += "\n"
    
    faq_content += "## Üniversitenin servis hizmeti var mı?\n\n"
    if university_services and university_services.get("shuttles", []):
        faq_content += "Evet, üniversitemiz aşağıdaki güzergahlarda servis hizmeti sunmaktadır:\n"
        for shuttle in university_services.get("shuttles", []):
            location = shuttle.get("location", "")
            time = shuttle.get("time", "")
            notes = shuttle.get("notes", "")
            
            faq_content += f"- {location}: {time}"
            if notes:
                faq_content += f" ({notes})"
            faq_content += "\n"
    else:
        faq_content += "Üniversitemizin belirli güzergahlarda servis hizmetleri bulunmaktadır. Güncel servis saatleri için üniversite ulaşım ofisiyle iletişime geçebilirsiniz.\n"
    faq_content += "\n"
    
    faq_content += "## Üniversiteye en yakın havalimanı hangisidir?\n\n"
    airports = []
    for method in transportation_methods:
        if method.get("method_name") == "Havalimanından":
            airports = method.get("airports", [])
    
    if airports:
        closest_airport = airports[0].get("name", "") if airports else ""
        closest_duration = airports[0].get("duration", "") if airports else ""
        faq_content += f"Üniversitemize en yakın havalimanı {closest_airport}'dır. Taksi ile yaklaşık {closest_duration} sürmektedir.\n\n"
    else:
        faq_content += "Üniversitemize en yakın havalimanı Sabiha Gökçen Havalimanı'dır. Taksi ile yaklaşık 20 dakika sürmektedir.\n\n"
    
    faq_content += "## Kampüsün çalışma saatleri nedir?\n\n"
    if working_hours:
        faq_content += f"Kampüsümüz {working_hours.get('days', '')} günleri {working_hours.get('hours', '')} saatleri arasında hizmet vermektedir.\n\n"
    else:
        faq_content += "Kampüsümüz genellikle Pazartesi-Cuma günleri mesai saatleri içinde hizmet vermektedir. Özel durumlar için üniversite ile iletişime geçebilirsiniz.\n\n"
    
    faq_content += "## Otobüs ile hangi hatları kullanabilirim?\n\n"
    bus_lines = []
    bus_stop = ""
    for method in transportation_methods:
        if method.get("method_name") == "Otobüs":
            bus_lines = method.get("lines", [])
            bus_stop = method.get("stop_name", "")
    
    if bus_lines:
        faq_content += f"Üniversitemize ulaşmak için {', '.join(bus_lines)} numaralı otobüs hatlarını kullanabilirsiniz. {bus_stop}'nda inmeniz gerekmektedir.\n\n"
    else:
        faq_content += "Üniversitemize ulaşmak için çeşitli İETT hatlarını kullanabilirsiniz. Detaylı bilgi için üniversite ulaşım ofisiyle iletişime geçebilirsiniz.\n\n"
    
    # SSS dokümanı oluştur
    faq_hash = compute_hash(faq_content)
    documents.append(Document(
        page_content=faq_content,
        metadata={
            "hash": faq_hash,
            "title": f"{university_name} Ulaşım Sıkça Sorulan Sorular",
            "university": university_name,
            "source": source_file,
            "document_type": "ulasim_sss",
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    return documents