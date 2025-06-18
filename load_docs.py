import json
from langchain.schema import Document
import hashlib

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



def compute_hash(content: str) -> str : 
    """
    Duplicate sorununu ortadan kaldirmak icin (dataya her yeni veri
    geldikten sonra guncelledigimizde eski datalarin tekrar
    yuklenmemesini saglamak icin) her dataya bir id atiyor hash ile.
    """
    return hashlib.sha256(content.encode("utf-8")).hexdigest()



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
    }
    docs = []
    for item in data:
        t = item.get("type")
        handler = handlers.get(t)

        if handler: 
            content = handler(item)
        else : 
            content = f"Bilinmeyen tipte veri {t}"

        # İçeriğin hash değerini hesapla (tekrarları önlemek için)
        doc_hash = compute_hash(content)
        # Varsa tag listesini al, yoksa boş liste
        tags = item.get("tags", [])
        
        # Document nesnesi oluştur, sayfa içeriği ve metadata (hash, taglar, tip) ekle
        docs.append(Document(page_content=content, metadata={"hash": doc_hash, 
                                                             "tags": tags,
                                                             "type": item.get("type")}))
    return docs 
