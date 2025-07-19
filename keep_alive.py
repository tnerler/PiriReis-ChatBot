import time
import requests

target = "https://chatbot.pirireis.edu.tr"

while True:
    try:
        response = requests.get(target, timeout=10)
        if response.status_code == 200:
            print("✅ Sunucu çalışıyor.")
        else:
            print(f"⚠️ HTTP yanıt kodu: {response.status_code}")
    except Exception as e:
        print("❌ Sunucuya ulaşılamıyor:", e)

    time.sleep(60)
