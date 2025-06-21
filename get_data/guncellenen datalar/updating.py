from bs4 import BeautifulSoup
import requests
import urllib.parse
import json 

def okul_duyurusu():
    BASE = "https://pirireis.edu.tr"
    URL = f"{BASE}/hakkimizda/duyuru/"
    

    
    r = requests.get(URL)
    soup = BeautifulSoup(r.content, "html5lib")



    pagination = soup.find("ul", class_="pagination")
    if not pagination : 
        print("Pagination bulunamadı, sadece ilk sayfa çekilecek.")
        toplam_sayfa = 1 
    else : 
        sayfa_numaralari = pagination.find_all("a")
        sayfa_sayilari = []
        for a in sayfa_numaralari : 
            try : 
                sayfa_no = int(a.text.strip())
                sayfa_sayilari.append(sayfa_no)
            except : 
                continue
        toplam_sayfa = max(sayfa_sayilari) if sayfa_sayilari else 1
    print(f"Toplam sayfa sayısı: {toplam_sayfa}")

    
    quotes = []
    for sayfa_no in range(1, toplam_sayfa + 1):
        url = f"{BASE}/hakkimizda/duyuru/page/{sayfa_no}"
        print(f"{sayfa_no}. sayfa çekiliyor: {url}")

        r = requests.get(url)
        soup = BeautifulSoup(r.content, "html5lib")

        cards = soup.select("div.col-12.col-md-4") + soup.select("div.col-12.col-md-8") + soup.select("div.col-6.col-md-3")
        for card in cards : 

            baslik_tag = card.find("div", class_="Card__Heading")
            if not baslik_tag:
                baslik_tag = card.find("h4", class_="Item__Heading")
            baslik = baslik_tag.text.strip() if baslik_tag else "Baslik yok"


            tarih_tag = card.find("span", class_="Card__Date")
            tarih = tarih_tag.text.strip() if tarih_tag else "Tarih yok"


            link_tag = card.find("a")
            if link_tag and link_tag.has_attr('href'):
                link = link_tag['href']

            quotes.append({
                "title": baslik,
                "tarih": tarih,
                "link": link
            }) 
    try : 
        with open("get_data\\guncellenen datalar\\okul_duyurusu.json", "w", encoding="utf-8") as f :
            json.dump(quotes, f, ensure_ascii=False, indent=4)
    except FileNotFoundError:
        print("Json Dosyasi yok!")



if __name__ == "__main__":
    okul_duyurusu()
    
