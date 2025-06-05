# Dockerfile

# 1. Base image olarak Python 3.12-slim kullanıyoruz (hafif, küçük boyutlu)
FROM python:3.12-slim

# 2. Container içindeki çalışma dizinini /app olarak belirleyelim
WORKDIR /app

# 3. Yerel makinedeki proje dosyalarını container içindeki /app dizinine kopyala
#    .dockerignore dosyasındaki ignore kurallarına uyarak gereksizleri atlar
COPY . /app

# 4. (Opsiyonel) Eğer bir requirements.txt dosyanız varsa, şu satırları ekleyin:
# COPY requirements.txt /app/
# RUN pip install --no-cache-dir -r requirements.txt

# 5. Container’ın dış dünyada dinleyeceği portu belirtin (81)
EXPOSE 81

# 6. Container başladıktan sonra otomatik çalışacak komut
#    Burada Python scriptimizi arka planda run ederiz
CMD ["python", "server.py"]
