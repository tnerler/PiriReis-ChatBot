from langchain.schema import Document
import hashlib
from typing import List
from datetime import datetime

def compute_hash(content: str) -> str:
    """İçeriğin benzersiz hash değerini hesaplar."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def process_data(data: dict, source_file: str) -> List[Document]:
    """
    Diploma Eki JSON verisini işleyerek Document nesneleri oluşturur.
    
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
    current_date = "2025-07-29 11:02:07"
    user_login = "tnerler"
    
    # Temel bilgileri al
    title = data.get("title", "Diploma Eki")
    description = data.get("description", "")
    benefits = data.get("benefits", {})
    student_benefits = benefits.get("for_students", [])
    institution_benefits = benefits.get("for_institutions", [])
    metadata = data.get("metadata", {})
    
    # Ana doküman içeriği oluştur
    full_content = f"# {title}\n\n"
    
    # Açıklama
    if description:
        full_content += f"{description}\n\n"
    
    # Öğrenci faydaları
    if student_benefits:
        full_content += "## Diploma Eki'nin Öğrenciler için faydaları\n\n"
        for i, benefit in enumerate(student_benefits, 1):
            full_content += f"{i}. {benefit}\n"
        full_content += "\n"
    
    # Kurum faydaları
    if institution_benefits:
        full_content += "## Diploma Eki'nin Yükseköğretim Kurumları için faydaları\n\n"
        for i, benefit in enumerate(institution_benefits, 1):
            full_content += f"{i}. {benefit}\n"
        full_content += "\n"
    
    # Ana dokümanı oluştur
    main_hash = compute_hash(full_content)
    documents.append(Document(
        page_content=full_content,
        metadata={
            "hash": main_hash,
            "title": title,
            "source": source_file,
            "document_type": "diploma_eki_tam",
            "file_name": metadata.get("file_name", source_file.split("/")[-1] if "/" in source_file else source_file),
            "processed_date": current_date,
            "processed_by": user_login,
            "student_benefits_count": len(student_benefits),
            "institution_benefits_count": len(institution_benefits)
        }
    ))
    
    # Öğrenci rehberi dokümanı
    student_content = f"# {title} - Öğrenci Rehberi\n\n"
    student_content += "Bu belge, Diploma Eki ve öğrencilere sağladığı faydalar hakkında bilgiler içermektedir.\n\n"
    
    # Diploma Eki tanımı
    if description:
        student_content += "## Diploma Eki Nedir?\n\n"
        student_content += f"{description}\n\n"
    
    # Öğrenci faydaları detaylı açıklama
    if student_benefits:
        student_content += "## Diploma Eki'nin Öğrencilere Sağladığı Faydalar\n\n"
        for i, benefit in enumerate(student_benefits, 1):
            student_content += f"### {i}. {benefit}\n\n"
            
            # Her fayda için detaylı açıklama ekle
            if i == 1:  # Yurtdışında tanınma
                student_content += "Diploma Eki, mezunların sahip olduğu yeterlilikleri uluslararası düzeyde anlaşılabilir kılar. "
                student_content += "Böylece farklı ülkelerdeki eğitim kurumları ve işverenler, mezunun aldığı eğitimin içeriği ve "
                student_content += "düzeyi hakkında net bir görüşe sahip olurlar.\n\n"
            elif i == 2:  # Yeterliliklerin tanımı
                student_content += "Diploma Eki, mezunun eğitim süreci boyunca edindiği tüm bilgi, beceri ve yetkinlikleri "
                student_content += "ayrıntılı şekilde belgelendirir. Bu, mezunun profili hakkında kapsamlı bir resim sunar.\n\n"
            elif i == 3:  # Tarafsız ifade
                student_content += "Diploma Eki, öğrencinin başarılarını objektif kriterler çerçevesinde değerlendirir ve "
                student_content += "standart bir formatta sunar. Bu standartlaştırılmış belge, değerlendirme süreçlerinde "
                student_content += "tarafsızlığı sağlar.\n\n"
            elif i == 4:  # İş ve eğitim olanakları
                student_content += "Diploma Eki, yurtdışındaki işverenler ve eğitim kurumları tarafından kolayca anlaşılabilir olduğundan, "
                student_content += "mezunların uluslararası iş başvurularında veya ileri düzey eğitim programlarına başvurularında "
                student_content += "avantaj sağlar.\n\n"
            elif i == 5:  # İstihdam edilebilirlik
                student_content += "Diploma Eki, mezunun sahip olduğu yetkinlikleri açık ve anlaşılır bir şekilde belgelendirerek, "
                student_content += "iş arayanların yeteneklerini potansiyel işverenlere daha etkili bir şekilde sunabilmesine "
                student_content += "olanak tanır.\n\n"
    
    # Diploma Eki alma süreci
    student_content += "## Diploma Eki Nasıl Alınır?\n\n"
    student_content += "Diploma Eki, mezuniyet işlemleri tamamlandıktan sonra diplomanız ile birlikte otomatik olarak düzenlenir. "
    student_content += "Türkiye'deki yükseköğretim kurumları, mezunlarına herhangi bir başvuru gerekmeksizin ve ücretsiz olarak "
    student_content += "Diploma Eki vermekle yükümlüdür.\n\n"
    student_content += "Diploma Eki'nin içeriği şu bilgileri içerir:\n\n"
    student_content += "1. Diploma sahibinin kimlik bilgileri\n"
    student_content += "2. Yükseköğretim derecesinin niteliği, düzeyi ve amacı\n"
    student_content += "3. Derecenin içerdiği çalışma alanları ve başarı düzeyi\n"
    student_content += "4. Mezunun elde ettiği yeterlilikler ve bu yeterliliklerin kullanılabileceği alanlar\n"
    student_content += "5. Diploma Eki'nin amacına ilişkin ek bilgiler\n\n"
    
    # Sık Sorulan Sorular
    student_content += "## Sık Sorulan Sorular\n\n"
    student_content += "**S: Diploma Eki için ayrıca başvuru yapmam gerekir mi?**\n\n"
    student_content += "C: Hayır, Diploma Eki mezuniyet işlemleriniz tamamlandığında diplomanızla birlikte verilir.\n\n"
    
    student_content += "**S: Diploma Eki ücretli midir?**\n\n"
    student_content += "C: Hayır, Diploma Eki ücretsiz olarak verilmektedir.\n\n"
    
    student_content += "**S: Diploma Eki hangi dilde düzenlenir?**\n\n"
    student_content += "C: Diploma Eki İngilizce olarak düzenlenir.\n\n"
    
    student_content += "**S: Daha önce mezun oldum ve Diploma Eki almadım, nasıl alabilirim?**\n\n"
    student_content += "C: Öğrenci işleri birimine başvurarak talep edebilirsiniz.\n\n"
    
    # Öğrenci rehberi dokümanını oluştur
    student_hash = compute_hash(student_content)
    documents.append(Document(
        page_content=student_content,
        metadata={
            "hash": student_hash,
            "title": "Diploma Eki - Öğrenci Rehberi",
            "source": source_file,
            "document_type": "diploma_eki_rehber",
            "audience": "öğrenciler",
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    # Kurum rehberi dokümanı
    institution_content = f"# {title} - Kurum Rehberi\n\n"
    institution_content += "Bu belge, Diploma Eki ve yükseköğretim kurumlarına sağladığı faydalar hakkında bilgiler içermektedir.\n\n"
    
    # Diploma Eki tanımı
    if description:
        institution_content += "## Diploma Eki Nedir?\n\n"
        institution_content += f"{description}\n\n"
    
    # Kurum faydaları detaylı açıklama
    if institution_benefits:
        institution_content += "## Diploma Eki'nin Kurumlara Sağladığı Faydalar\n\n"
        for i, benefit in enumerate(institution_benefits, 1):
            institution_content += f"### {i}. {benefit}\n\n"
            
            # Her fayda için detaylı açıklama ekle
            if i == 1:  # Akademik ve mesleki tanınma
                institution_content += "Diploma Eki, kurumunuzun verdiği derecelerin uluslararası alanda daha kolay tanınmasını sağlar. "
                institution_content += "Bu sayede mezunlarınızın aldığı eğitimin kalitesi ve içeriği konusunda şeffaflık sağlanır.\n\n"
            elif i == 2:  # Ortak çerçeve
                institution_content += "Avrupa Yükseköğrenim Alanı içinde ortak bir format sunarken, kurumunuzun özgün yapısını ve "
                institution_content += "programlarını koruma imkanı verir. Standardizasyon ve özgünlük arasında denge kurar.\n\n"
            elif i == 3:  # Yeterliliklerin değerlendirilmesi
                institution_content += "Farklı ülkelerdeki eğitim kurumlarının ve işverenlerin, mezunlarınızın sahip olduğu "
                institution_content += "yeterlilikleri doğru değerlendirmelerine olanak tanır.\n\n"
            elif i == 4:  # Uluslararası bilinirlik
                institution_content += "Kurumunuzun uluslararası görünürlüğünü ve bilinirliğini artırır, böylece uluslararası "
                institution_content += "öğrenci çekme potansiyelinizi yükseltir.\n\n"
            elif i == 5:  # İstihdam edilebilirlik
                institution_content += "Mezunlarınızın ulusal ve uluslararası iş piyasasında daha avantajlı konumda olmalarını sağlar, "
                institution_content += "bu da kurumunuzun tercih edilirliğini artırır.\n\n"
            elif i == 6:  # İdari sorunlara çözüm
                institution_content += "Diploma denkliği ve tanınma konularında yaşanan sorunları azaltarak, idari personelin "
                institution_content += "iş yükünü hafifletir ve süreçleri hızlandırır.\n\n"
    
    # Diploma Eki düzenleme süreci
    institution_content += "## Diploma Eki Düzenleme Süreci\n\n"
    institution_content += "Diploma Eki düzenlemek için şu adımlar izlenir:\n\n"
    institution_content += "1. **Hazırlık:** Mezunların bilgilerinin ve transkriptlerinin derlenmesi\n"
    institution_content += "2. **Format Kontrolü:** Avrupa Komisyonu tarafından belirlenen standart formata uygunluk kontrolü\n"
    institution_content += "3. **Çeviri:** Program içeriklerinin İngilizce çevirilerinin hazırlanması\n"
    institution_content += "4. **Doğrulama:** Bilgilerin doğruluğunun kontrol edilmesi\n"
    institution_content += "5. **Basım ve İmza:** Belgenin basımı ve yetkililerce imzalanması\n"
    institution_content += "6. **Teslim:** Diploma ile birlikte mezuna teslim edilmesi\n\n"
    
    institution_content += "## Diploma Eki Label (Etiketi)\n\n"
    institution_content += "Avrupa Komisyonu tarafından verilen 'Diploma Supplement Label (DS Label)' etiketi, Diploma Eki'ni "
    institution_content += "doğru ve eksiksiz bir şekilde düzenleyen kurumlara verilir. Bu etiket, kurumunuzun Avrupa "
    institution_content += "standartlarına uygun olarak Diploma Eki verdiğinin bir göstergesidir ve uluslararası prestij sağlar.\n\n"
    
    institution_content += "DS Label almak için kurumunuzun Diploma Eki düzenleme süreçlerinin Avrupa Komisyonu tarafından "
    institution_content += "değerlendirilmesi ve onaylanması gerekmektedir.\n\n"
    
    # Kurum rehberi dokümanını oluştur
    institution_hash = compute_hash(institution_content)
    documents.append(Document(
        page_content=institution_content,
        metadata={
            "hash": institution_hash,
            "title": "Diploma Eki - Kurum Rehberi",
            "source": source_file,
            "document_type": "diploma_eki_rehber",
            "audience": "kurumlar",
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    # Karşılaştırmalı analiz dokümanı
    comparative_content = "# Diploma Eki ve Diğer Uluslararası Belgeler Karşılaştırması\n\n"
    comparative_content += "Bu belge, Diploma Eki ile diğer uluslararası belgelerin karşılaştırmasını içermektedir.\n\n"
    
    comparative_content += "## Diploma Eki ve Diğer Belgelerin Karşılaştırılması\n\n"
    comparative_content += "| Özellik | Diploma Eki | Transkript | Denklik Belgesi | Apostil |\n"
    comparative_content += "|---------|-------------|------------|-----------------|--------|\n"
    comparative_content += "| **Amaç** | Eğitim içeriğini ve seviyesini açıklar | Not dökümünü gösterir | Eğitim denkliğini onaylar | Belge gerçekliğini onaylar |\n"
    comparative_content += "| **İçerik** | Program detayları ve kazanılan yetkinlikler | Alınan dersler ve notlar | Denklik değerlendirme sonucu | Belgeyi onaylayan resmi mühür |\n"
    comparative_content += "| **Verildiği Kurum** | Eğitim kurumu | Eğitim kurumu | Ulusal eğitim otoritesi | Noter veya dışişleri |\n"
    comparative_content += "| **Geçerlilik** | Uluslararası | Ulusal/Uluslararası | Ulusal | Uluslararası |\n"
    comparative_content += "| **Dil** | İngilizce (genellikle) | Ulusal dil/İngilizce | Ulusal dil | Ulusal dil |\n"
    comparative_content += "| **Ücret** | Ücretsiz | Genellikle ücretsiz | Ücretli | Ücretli |\n"
    
    comparative_content += "\n## Diploma Eki'nin Avantajları\n\n"
    comparative_content += "Diğer belgelere kıyasla Diploma Eki'nin avantajları şunlardır:\n\n"
    comparative_content += "- **Kapsamlı Bilgi:** Sadece notları değil, program içeriği ve kazanılan yetkinlikleri de içerir\n"
    comparative_content += "- **Standartlaştırılmış Format:** Avrupa genelinde tanınan ortak bir formatta hazırlanır\n"
    comparative_content += "- **Otomatik Verilme:** Mezuniyet sonrası ek başvuru gerekmeden otomatik olarak verilir\n"
    comparative_content += "- **Ücretsiz Olması:** Öğrenciye herhangi bir mali yük getirmez\n"
    comparative_content += "- **Çift Dilli Olabilmesi:** Hem ulusal dilde hem de İngilizce olarak düzenlenebilir\n\n"
    
    comparative_content += "## Avrupa Yükseköğrenim Alanı'ndaki Diğer Araçlarla İlişkisi\n\n"
    comparative_content += "Diploma Eki, Avrupa Yükseköğrenim Alanı'nda kullanılan diğer araçlarla birlikte çalışır:\n\n"
    comparative_content += "- **AKTS (Avrupa Kredi Transfer Sistemi):** Öğrenci iş yükünü ölçen standart bir kredi sistemi\n"
    comparative_content += "- **Yeterlilikler Çerçevesi:** Eğitim düzeylerini tanımlayan ulusal ve Avrupa çerçeveleri\n"
    comparative_content += "- **Kalite Güvencesi:** Yükseköğretim kurumlarının kalite standartlarını sağlama süreçleri\n\n"
    
    comparative_content += "Bu araçlar bir arada, Avrupa Yükseköğrenim Alanı içinde hareketliliği ve mezunların yeterliliklerinin tanınmasını kolaylaştırır.\n"
    
    # Karşılaştırma dokümanını oluştur
    comparative_hash = compute_hash(comparative_content)
    documents.append(Document(
        page_content=comparative_content,
        metadata={
            "hash": comparative_hash,
            "title": "Diploma Eki Karşılaştırmalı Analizi",
            "source": source_file,
            "document_type": "diploma_eki_analiz",
            "processed_date": current_date,
            "processed_by": user_login
        }
    ))
    
    return documents