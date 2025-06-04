import json
from langchain.schema import Document

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
        List[Document]: İçeriğinde soru-cevap veya bilgi metinleri bulunan Document nesneleri listesi.
    """


    with open("get_data/data.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # Her soru-cevap cifti icin Document olustur
    docs = []
    for item in data:
        if item.get("type") == "soru-cevap":
            content= f"Soru: {item['soru']}\nCevap: {item['cevap']}"
        else:
            content=f"Bilgi: {item['context']}"
        docs.append(Document(page_content=content))
    return docs 
