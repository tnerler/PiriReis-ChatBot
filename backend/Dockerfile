# backend/Dockerfile
FROM python:3.11

# Çalışma dizinini ayarla
WORKDIR /app

# Gereksinimleri kopyala ve kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# .env dosyasını da konteyner içine al (opsiyonel)
# COPY .env .env

# Portu belirt (Flask default 5000)
EXPOSE 5000

# Flask uygulamasını çalıştır
CMD ["python", "app.py"]
