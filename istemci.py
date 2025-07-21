import os
import time

while True:
    print("Chatbot başlatılıyor...")
    os.system("python app.py")  # Veya uvicorn app:app --host 0.0.0.0 --port 8000
    print("30 dakika bekleniyor...")
    time.sleep(1800)  # 30 dakika = 1800 saniye
