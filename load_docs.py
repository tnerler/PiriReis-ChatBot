import json
from langchain.schema import Document
import hashlib


def compute_hash(content: str) -> str : 
    """
    Duplicate sorununu ortadan kaldirmak icin (dataya her yeni veri
    geldikten sonra guncelledigimizde eski datalarin tekrar
    yuklenmemesini saglamak icin) her dataya bir id atiyor hash ile.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def soru_cevap(item) : 
    content = f"Soru: {item['soru']}\nCevap: {item['cevap']}"
    return content

def bolumler(item):
    bolum_listesi = item.get("departments", [])
    tum_bolumler = []

    for bolum in bolum_listesi:
        content = f"Bölüm: {bolum['name']}\n {bolum['name']} hakkında daha fazla bilgi için Link: {bolum['link']}"
        tum_bolumler.append(content)

    return "\n\n".join(tum_bolumler)

def comp_kadro(item) : 
    content = f"Bilgisayar Mühendisliği Kadrosu: {item['context']}"
    return content

def bilgi(item) : 
    content=f"Bilgi: {item['context']}"
    return content

def staj(item) : 
    content = f"Bölüm: {item['bolum']}\nBilgi:{item['context']}"
    return content

def universite_kadrosu(item): 
    content = "Üniversite Kadrosu:\n\n" + "\n".join(item["context"])
    return content

def comp_ders_icerigi(item):
    bolum_adi = item.get("bolum_adi", "Bölüm Bilgisi Yok")
    fakulte_adi = item.get("fakulte_adi", "")
    universite_adi = item.get("universite_adi", "")
    
    # Başlık kısmı
    content = f"{universite_adi} - {fakulte_adi} - {bolum_adi} Ders İçerikleri:\n"

    # Yarıyılları gez
    for yariyil in item.get("yariyillar", []):
        content += f"\n{yariyil['yariyil_no']}. Yarıyıl\n"
        
        # Her bir dersin bilgilerini ekle
        for ders in yariyil.get("dersler", []):
            content += (
                f"\n{ders['ders_kodu']} - {ders['ders_adi']} ({ders['kredi']}) | AKTS: {ders['akts']}\n"
                f"Ders İçeriği: {ders['ders_icerigi']}\n"
            )
            
            # Kaynaklar kısmını ekle
            kaynaklar = ders.get("kaynaklar", {})
            ders_kitaplari = kaynaklar.get("ders_kitaplari", [])
            yardimci_kitaplar = kaynaklar.get("yardimci_kitaplar", [])
            
            # Ders kitaplarını listele
            if ders_kitaplari:
                content += "Ders Kitapları:\n"
                for kitap in ders_kitaplari:
                    content += f"- {kitap}\n"

            # Yardımcı kitapları listele
            if yardimci_kitaplar:
                content += "Yardımcı Kaynaklar:\n"
                for kitap in yardimci_kitaplar:
                    content += f"- {kitap}\n"

    return content

def duyurular(item):
    return f"Duyuru: {item['title']}\nLink: {item['link']}"


def pru_ders_koordinasyonu_yönetmeliği(item) : 
    context_list = item["context"]
    context_text = " ".join(context_list)  # Listeyi düz metne çevir
    return f"Ders koordinasyonu yonetmeligi : {context_text}"

def pru_EK_sınav_hakkı(item) : 
    context_list = item["context"]
    context_text = " ".join(context_list)  # Listeyi düz metne çevir
    return f"EK_sınav_hakkı: {context_text}"

def pru_ingilizce_hazırlık_yönetmeliği(item) :
    context_list = item["context"]
    context_text = " ".join(context_list)  # Listeyi düz metne çevir 
    return f"ingilizce_hazırlık_yönetmeliği: {context_text}"

def pru_lisans_önlisans_eğitim_öğretim_sınav_yönetmeliği(item) : 
    context_list = item["context"]
    context_text = " ".join(context_list)  # Listeyi düz metne çevir
    return f"lisans_önlisans_eğitim_öğretim_sınav_yönetmeliği: {context_text}"

def pru_Üniforma_yönetmeliği(item) : 
    context_list = item["context"]
    context_text = " ".join(context_list)  # Listeyi düz metne çevir
    return f"Üniforma_yönetmeliği: {context_text}"

def piri_reis_brosur(item) : 
    context_list = item["context"]
    context_text = " ".join(context_list)  # Listeyi düz metne çevir
    return f"Piri Reis Öğrenci Broşürü: {context_text}"



def fakulte_dersleri_0(json_data):
    """
    Tüm fakülte ders bilgilerini otomatik olarak load_docs listesine ekler
    """
    load_docs =[]
    for fakulte_key, fakulte_data in json_data.items():
        if 'fakulte_adi' in fakulte_data and 'dersler' in fakulte_data:
            content = f"Fakülte: {fakulte_data['fakulte_adi']}\n\n"
            content += "DERS LİSTESİ:\n"
            content += "=" * 50 + "\n\n"
            
            for ders in fakulte_data['dersler']:
                content += f"Ders Kodu: {ders['ders_kodu']}\n"
                content += f"Ders Adı: {ders['ders_adi']}\n"
                content += f"Teorik (T): {ders['T']} saat\n"
                content += f"Uygulama (U): {ders['U']} saat\n"
                content += f"Laboratuvar (L): {ders['L']} saat\n"
                content += f"Kredi: {ders['kredi']}\n"
                content += f"AKTS: {ders['akts']}\n"
                content += "-" * 30 + "\n\n"
            
            load_docs.append(content)
    return load_docs


def denizcilik_fakultesi(item) : 
    content = item["context"]
    return content

def denizcilik_meslek_yuksekokulu(item) : 
    content = item["context"]
    return content

def hukuk_fakultesi(item) : 
    content = item["context"]
    return content

def bilgisayar_muhendisligi(item) : 
    content = item["context"]
    return content

def elektrik_elektronik_muhendisligi(item) : 
    content = item["context"]
    return content

def endustri_muhendisligi(item) : 
    content = item["context"]
    return content

def muhendislik_fakultesi(item) : 
    content = item["context"]
    return content

def load_docs() : 
    """
    JSON dosyasından verileri yükler ve LangChain Document formatına dönüştürür.

    İşleyiş:
    1. "get_data/data.json" dosyasını UTF-8 kodlamasıyla açar ve JSON formatında okur.
    2. İçindeki her öğeyi kontrol eder:
       - Eğer "type" alanı "soru-cevap" ise:
         Soru ve cevabı "Soru: ...\nCevap: ..." formatında bir metin haline getirir.
       - Diğer durumlarda (örneğin "bilgi" türü) "context" alanını "Bilgi: ..." olarak metne ekler.
    3. Her metni bir Document nesnesi olarak docs listesine ekler.
    4. Tüm kayıtları Document listesi olarak döner.

    Varsayım:
    - "soru-cevap" tipindeki kayıtlar mutlaka "soru" ve "cevap" alanlarına sahiptir.
    - Diğer tipler ise mutlaka "context" alanına sahiptir.

    Returns:
        List[Document]: İçeriğinde soru-cevap veya bilgi metinleri ve hash id'lerin bulundugu Document nesneleri listesi.
    """
    
    try: 
        with open("get_data/main_data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError: 
        print("Dosya Bulunamadi.")


    try:
        with open("get_data/ders_kredileri.json", "r", encoding="utf-8") as f:
            ders_data = json.load(f)

    except FileNotFoundError:
        print("fakulte_dersleri.json dosyası bulunamadı.")
        ders_data = {}

    # Her soru-cevap cifti icin Document olustur
    handlers = {
    "soru-cevap": soru_cevap,
    "bolumler": bolumler,
    "comp_kadro": comp_kadro,
    "bilgi": bilgi,
    "staj": staj,
    "comp_ders_icerigi" : comp_ders_icerigi,
    "universite_kadrosu" : universite_kadrosu,
    "duyurular": duyurular,
    "PRU_ders_koordinasyonu_yönetmeliği" : pru_ders_koordinasyonu_yönetmeliği,
    "PRU_EK_sınav_hakkı" : pru_EK_sınav_hakkı,
    "PRU_ingilizce_hazırlık_yönetmeliği" : pru_ingilizce_hazırlık_yönetmeliği,
    "PRU_lisans_önlisans_eğitim_öğretim_sınav_yönetmeliği": pru_lisans_önlisans_eğitim_öğretim_sınav_yönetmeliği,
    "PRU_Üniforma_yönetmeliği" : pru_Üniforma_yönetmeliği,
    "piri_reis_brosur": piri_reis_brosur,
    "Denizcilik_Fakültesi_pdf.docx" : denizcilik_fakultesi,
    "Denizcilik_Meslek_Yüksekokulu_pdf.docx" : denizcilik_meslek_yuksekokulu,
    "Hukuk_Fakültesi_pdf.docx" : hukuk_fakultesi,
    "Lisans_BilgisayarMühendisliği_pdf.docx" : bilgisayar_muhendisligi,
    "Lisans_ElektrikElektronikMühendisliği_pdf.docx" : elektrik_elektronik_muhendisligi,
    "Lisans_Endüstri_Mühendisliği_pdf.docx" : endustri_muhendisligi,
    "Mühendislik_Fakültesi_pdf.docx" : muhendislik_fakultesi,
    }

    docs = []
    for item in data:
        t = item.get("type")
        handler = handlers.get(t)

        if handler: 
            content = handler(item)
        else : 
            content = f"{t}"

        # İçeriğin hash değerini hesapla (tekrarları önlemek için)
        doc_hash = compute_hash(content)
        # Varsa tag listesini al, yoksa boş liste
        tags = item.get("tags", [])
        
        # Document nesnesi oluştur, sayfa içeriği ve metadata (hash, taglar, tip) ekle
        docs.append(Document(page_content=content, metadata={"hash": doc_hash, 
                                                             "tags": tags,
                                                             "type": item.get("type")}))
        
    

    ders_metni_listesi = fakulte_dersleri_0(ders_data)
    for metin in ders_metni_listesi:
        doc_hash = compute_hash(metin)
        docs.append(Document(page_content=metin, metadata={"hash": doc_hash, "tags": ["ders"], "type": "fakulte_dersleri"}))
        
    return docs 
