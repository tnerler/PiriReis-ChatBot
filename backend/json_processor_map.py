from backend.load_documents.load_denizcilik_fakultesi import process_data as process_denizcilik_json
from backend.load_documents.load_dmyo import process_data as process_dmyo_json
from backend.load_documents.load_het import process_data as process_het_json
from backend.load_documents.load_hukuk import process_data as process_hukuk_json
from backend.load_documents.load_iibf import process_data as process_iibf_json
from backend.load_documents.load_kisiler import process_data as process_people_json
from backend.load_documents.load_muhendislik import process_data as process_muhendislik_json
from backend.load_documents.load_ders_koordinasyonlugu import process_data as process_ders_koordinasyonu_json       
from backend.load_documents.load_ek_sinav_hakki import process_data as process_ek_sinav_hakki_json
from backend.load_documents.load_ingilizce_hazirlik_yonetmeligi import process_data as process_ingilizce_yonetmeligi_json   
from backend.load_documents.load_lisans_onlisans_egitim_sinav_yonetmeligi import process_data as process_lisans_onlisans_json
from backend.load_documents.load_uniforma_yonetmeligi import process_data as process_uniforma_yonetmeligi_json
from backend.load_documents.load_erasmus_universiteleri import process_data as process_erasmus_json
from backend.load_documents.load_kampus_olanaklari import process_data as process_kampus_json
from backend.load_documents.load_siralamalar import process_data as process_siralamalar_json
from backend.load_documents.load_ulasim import process_data as process_ulasim_json
from backend.load_documents.load_burslar import process_data as process_burslar_json
from backend.load_documents.load_sik_sorulan_sorular import process_data as process_sik_sorulan_sorular_json
from backend.load_documents.load_pru_brosur import process_data as process_pru_brosur_md
from backend.load_documents.load_proje_ofisi_koordinatorlugu import process_data as process_proje_ofisi_json
from backend.load_documents.load_teknopark import process_data as process_teknopark_json
from backend.load_documents.load_tezsiz_yuksek_lisans import process_data as process_tezsiz_yuksek_lisans_json
from backend.load_documents.load_tezli_yuksek_lisans import process_data as process_tezli_yuksek_lisans_json
from backend.load_documents.load_doktora_programlari import process_data as process_doktora_programlari_json
from backend.load_documents.load_ogrenciler_icin_bilgi import process_data as process_ogrenciler_bilgi_json
from backend.load_documents.load_diploma_eki import process_data as process_diploma_eki_json
from backend.load_documents.load_rektor import process_data as process_rektor_json
from backend.load_documents.load_ingilizce_hazirlik_takvim import process_data as process_ingilizce_hazirlik_takvim_json
from backend.load_documents.load_lisans_onlisans_akademik_takvim import process_data as process_lisans_onlisans_akademik_takvim_json
from backend.load_documents.load_lisansustu_egitim_enstitusu_akademik_takvim import process_data as process_lisansustu_egitim_enstitusu_akademik_takvim_json

json_processor_map = {
    "denizcilik_fakultesi.json": process_denizcilik_json,
    "dmyo.json": process_dmyo_json,
    "het.json": process_het_json,
    "hukuk.json": process_hukuk_json,
    "iibf.json": process_iibf_json,
    "kisiler.json": process_people_json,
    "muhendislik.json": process_muhendislik_json,
    "ders_koordinasyonlugu.json": process_ders_koordinasyonu_json,
    "pru_ek_sinav_hakki.json": process_ek_sinav_hakki_json,
    "ingilizce_hazirlik_yonetmeligi.json": process_ingilizce_yonetmeligi_json,
    "lisans_onlisans_egitim_sinav_yonetmeligi.json": process_lisans_onlisans_json,
    "uniforma_yonetmeligi.json": process_uniforma_yonetmeligi_json,
    "erasmus_universiteleri.json": process_erasmus_json,
    "kampus_olanaklari.json": process_kampus_json,
    "siralamalar.json": process_siralamalar_json,
    "ulasim.json": process_ulasim_json,
    "burslar.json": process_burslar_json,
    "sik_sorulan_sorular.json": process_sik_sorulan_sorular_json,
    "proje_ofisi_koordinatorlugu.json": process_proje_ofisi_json,
    "teknopark.json": process_teknopark_json,
    "tezsiz_yuksek_lisans.json": process_tezsiz_yuksek_lisans_json,
    "tezli_yuksek_lisans.json": process_tezli_yuksek_lisans_json,
    "doktora_programlari.json": process_doktora_programlari_json,
    "ogrenciler_icin_bilgiler.json": process_ogrenciler_bilgi_json,
    "diploma_eki.json": process_diploma_eki_json,
    "rektor.json": process_rektor_json,
    "ingilizce_hazirlik_takvim.json": process_ingilizce_hazirlik_takvim_json,
    "lisans_onlisans_akademik_takvim.json": process_lisans_onlisans_akademik_takvim_json,
    "lisansustu_egitim_enstitusu_akademik_takvim.json": process_lisansustu_egitim_enstitusu_akademik_takvim_json,
}