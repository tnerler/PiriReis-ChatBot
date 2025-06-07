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
        with open("get_data/data.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError: 
        print("Dosya Bulunamadi.")

    # Her soru-cevap cifti icin Document olustur
    docs = []
    for item in data:
        if item.get("type") == "soru-cevap":
            content= f"Soru: {item['soru']}\nCevap: {item['cevap']}"
    
        else:
            content=f"Bilgi: {item['context']}"
        
        doc_hash = compute_hash(content)
        docs.append(Document(page_content=content, metadata={"hash": doc_hash, 
                                                             "type": item.get("type")}))
    return docs 
