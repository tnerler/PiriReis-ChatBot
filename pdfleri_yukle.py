import os
import json
from PyPDF2 import PdfReader

# PDF klasörünün yolu
pdf_klasoru = "C:\\Users\\tuana\\OneDrive\\Masaüstü\\pdfler" 

veriler = {}



def pdfleri_yukle() :
    for dosya_adi in os.listdir(pdf_klasoru):
        if dosya_adi.endswith(".pdf"):
            pdf_yolu = os.path.join(pdf_klasoru, dosya_adi)
            reader = PdfReader(pdf_yolu)

            metin = ""
            for sayfa in reader.pages:
                metin += sayfa.extract_text() or ""

            # JSON'a ekleme (dosya adını key yapıyoruz)
            veriler[dosya_adi] = metin.strip()

    # JSON olarak kaydet
    with open("pdf_metinleri.json", "w", encoding="utf-8") as f:
        json.dump(veriler, f, ensure_ascii=False, indent=2)

def birlestir() :
    with open("get_data\\main_data.json", "r", encoding="utf-8") as f1:
        list1 = json.load(f1)

    with open("pdf_metinleri.json", "r", encoding="utf-8") as f2:
        list2 = json.load(f2)

    birlesik = list1 + list2

    with open("get_data\\main_data.json", "w", encoding="utf-8") as f:
        json.dump(birlesik, f, ensure_ascii=False, indent=2)

birlestir()