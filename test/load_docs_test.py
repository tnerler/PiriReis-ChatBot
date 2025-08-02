import json
from langchain.schema import Document
import hashlib
import os
from typing import List
import glob

# Tüm process_data fonksiyonlarını doğru _test uzantılı dosyalardan al
# Tüm process_data fonksiyonlarını doğru _test_test uzantılı dosyalardan al
from load_documents_test.load_denizcilik_fakultesi_test_test import process_data as process_denizcilik_json
from load_documents_test.load_dmyo_test_test import process_data as process_dmyo_json
from load_documents_test.load_het_test_test import process_data as process_het_json
from load_documents_test.load_hukuk_test_test import process_data as process_hukuk_json
from load_documents_test.load_iibf_test_test import process_data as process_iibf_json
from load_documents_test.load_kisiler_test_test import process_data as process_people_json
from load_documents_test.load_muhendislik_test_test import process_data as process_muhendislik_json
from load_documents_test.load_ders_koordinasyonlugu_test_test import process_data as process_ders_koordinasyonu_json
from load_documents_test.load_ek_sinav_hakki_test_test import process_data as process_ek_sinav_hakki_json
from load_documents_test.load_ingilizce_hazirlik_yonetmeligi_test_test import process_data as process_ingilizce_yonetmeligi_json
from load_documents_test.load_lisans_onlisans_egitim_sinav_yonetmeligi_test_test import process_data as process_lisans_onlisans_json
from load_documents_test.load_uniforma_yonetmeligi_test_test import process_data as process_uniforma_yonetmeligi_json
from load_documents_test.load_erasmus_universiteleri_test_test import process_data as process_erasmus_json
from load_documents_test.load_kampus_olanaklari_test_test import process_data as process_kampus_json
from load_documents_test.load_siralamalar_test_test import process_data as process_siralamalar_json
from load_documents_test.load_ulasim_test_test import process_data as process_ulasim_json
from load_documents_test.load_burslar_test_test import process_data as process_burslar_json
from load_documents_test.load_sik_sorulan_sorular_test_test import process_data as process_sik_sorulan_sorular_json
from load_documents_test.load_pru_brosur_test_test import process_data as process_pru_brosur_md
from load_documents_test.load_proje_ofisi_koordinatorlugu_test_test import process_data as process_proje_ofisi_json
from load_documents_test.load_teknopark_test_test import process_data as process_teknopark_json
from load_documents_test.load_tezsiz_yuksek_lisans_test_test import process_data as process_tezsiz_yuksek_lisans_json
from load_documents_test.load_tezli_yuksek_lisans_test_test import process_data as process_tezli_yuksek_lisans_json
from load_documents_test.load_doktora_programlari_test_test import process_data as process_doktora_programlari_json
from load_documents_test.load_ogrenciler_icin_bilgi_test_test import process_data as process_ogrenciler_bilgi_json
from load_documents_test.load_diploma_eki_test_test import process_data as process_diploma_eki_json


def compute_hash(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def identify_json_type(file_name: str) -> str:
    name = file_name.lower().replace(".json", "")
    return name  # dosya adının sonu _test olduğu için doğrudan işimize yarar

def load_docs() -> List[Document]:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(BASE_DIR, r"test/get_data_test")

    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    md_files = glob.glob(os.path.join(data_dir, "*.md"))

    all_docs = []
    processed_hashes = set()

    process_map = {
        "denizcilik_fakultesi_test": process_denizcilik_json,
        "dmyo_test": process_dmyo_json,
        "het_test": process_het_json,
        "hukuk_test": process_hukuk_json,
        "iibf_test": process_iibf_json,
        "kisiler_test": process_people_json,
        "muhendislik_test": process_muhendislik_json,
        "ders_koordinasyonlugu_test": process_ders_koordinasyonu_json,
        "pru_ek_sinav_hakki_test": process_ek_sinav_hakki_json,
        "ingilizce_hazirlik_yonetmeligi_test": process_ingilizce_yonetmeligi_json,
        "lisans_onlisans_egitim_sinav_yonetmeligi_test": process_lisans_onlisans_json,
        "uniforma_yonetmeligi_test": process_uniforma_yonetmeligi_json,
        "erasmus_universiteleri_test": process_erasmus_json,
        "kampus_olanaklari_test": process_kampus_json,
        "siralamalar_test": process_siralamalar_json,
        "ulasim_test": process_ulasim_json,
        "burslar_test": process_burslar_json,
        "sik_sorulan_sorular_test": process_sik_sorulan_sorular_json,
        "proje_ofisi_koordinatorlugu_test": process_proje_ofisi_json,
        "teknopark_test": process_teknopark_json,
        "tezsiz_yuksek_lisans_test": process_tezsiz_yuksek_lisans_json,
        "tezli_yuksek_lisans_test": process_tezli_yuksek_lisans_json,
        "doktora_programlari_test": process_doktora_programlari_json,
        "ogrenciler_icin_bilgi_test": process_ogrenciler_bilgi_json,
        "diploma_eki_test": process_diploma_eki_json,
    }

    for json_file in json_files:
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            file_name = os.path.basename(json_file)
            json_type = identify_json_type(file_name)
            print(f"[DEBUG] Loaded {file_name}")

            if json_type in process_map:
                docs = process_map[json_type](data, file_name)
                for doc in docs:
                    if doc.metadata["hash"] not in processed_hashes:
                        processed_hashes.add(doc.metadata["hash"])
                        all_docs.append(doc)
            else:
                print(f"[WARNING] Unknown file type: {json_type}, skipping...")

        except Exception as e:
            print(f"❌ Error processing {json_file}: {e}")

    for md_file in md_files:
        try:
            with open(md_file, "r", encoding="utf-8") as f:
                content = f.read()
            file_name = os.path.basename(md_file)
            print(f"[DEBUG] Loaded {file_name}")

            if "pru_brosur" in file_name:
                docs = process_pru_brosur_md(content, file_name)
                for doc in docs:
                    if doc.metadata["hash"] not in processed_hashes:
                        processed_hashes.add(doc.metadata["hash"])
                        all_docs.append(doc)
            else:
                print(f"[WARNING] Unknown MD type: {file_name}, skipping...")
        except Exception as e:
            print(f"❌ Error processing {md_file}: {e}")

    print(f"[i] Total {len(all_docs)} unique documents loaded")
    return all_docs