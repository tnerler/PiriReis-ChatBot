import requests
from bs4 import BeautifulSoup
import json

# Sayfa URL'si
url = "https://aday.pirireis.edu.tr/sikca-sorulan-sorular/"  # Gerçek linkle değiştir

headers = {
    "User-Agent": "Mozilla/5.0"
}
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

faq_list = []

# Tüm soru-cevap kutularını bul
faq_items = soup.select("div.Questions__Item.accordion-item")

for item in faq_items :
    question_tag = item.select_one("button.Question__Button.accordion-button.collapsed")
    question = question_tag.get_text(strip=True) if question_tag else ""
   
    answer_tag = item.select_one("div.Answer__Body.accordion-body")
    answer = answer_tag.get_text(strip=True) if answer_tag else ""
    

    if question and answer : 
        faq_list.append({
            "type" : 'soru-cevap',
            "soru" : question,
            "cevap" : answer
        })
with open("data.json", "w", encoding="utf-8") as f:
    json.dump(faq_list, f, ensure_ascii=False, indent=2)

print("✅ bilgiler eklendi.")