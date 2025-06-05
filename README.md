# 🚀 Basit HTTP Web Sunucusu (Python)

Bu proje, Python dilinde yazılmış basit bir HTTP web sunucusudur, `socket` ve `threading` modülleriyle geliştirilmiştir.

---
## 🎯 Amaç

* temel HTTP server geliştirmek
* Socket programlamayı uygulamalı olarak öğrenmek
* MIME tipleri, statik dosya sunumu, JSON API gibi temel web sunucu özelliklerini uygulamak
* Docker ile uygulamayı container hâline getirmeyi deneyimlemek

---
## ⚙️ Özellikler

* ✅ 81 portu üzerinden TCP bağlantı kabul eder
* ✅ Her bağlantı için yeni bir thread açar (çoklu bağlantı desteği)
* ✅ `GET` isteklerini işler, `/static` klasöründen dosya sunar
* ✅ `/api/hello` endpoint’i üzerinden JSON mesaj döner
* ✅ `POST /api/greet` ile kullanıcıdan ad/soyad alır, kişiye özel selam döner
* ✅ MIME tipi içerik başlığı doğru şekilde tanımlanır
* ✅ Her istek için loglama yapılır (`server.log` dosyasına)
* ✅ 404 gibi HTTP hata yanıtları desteklenir
* ✅ Basit route tanımlama sistemi vardır (`@route` decorator)
* ✅ Basit bir template engine içerir (`{{key}}` yer tutucu destekler)

---
## 📁 Proje Yapısı

```
/
├── server.py                # Ana sunucu kodu
├── static/                 # HTML, CSS, JS gibi statik dosyalar
│   ├── style.css
│   └── script.js
├── templates/              # HTML şablonları
│   └── index.html
├── server.log              # Otomatik oluşturulan istek logları
├── Dockerfile              # Docker için yapılandırma
├── .dockerignore           # Gereksiz dosyaları dışarıda bırakır
└── README.md               # Bu döküman
```

---

## 🚀 Nasıl Kullanılır?

### 1. Python ile çalıştırmak için:

```bash
python server.py
```

Sunucu [http://localhost:81](http://localhost:81) adresinde çalışır.

### 2. Docker ile çalıştırmak için:

```bash
docker build -t my-http-server .
docker run -p 8080:81 my-http-server
```

---
## 🌐 Kullanım Örnekleri

* `http://localhost:81/` → Ana sayfa (template engine ile)
* `http://localhost:81/static/style.css` → Statik dosya
* `http://localhost:81/api/hello` → JSON: `{ "message": "Hello, world!" }`
* `POST http://localhost:81/api/greet` → Gövde: `{ "name": "Emre", "surname": "Yıldız" }`

---
## 🛠️ Kullanılan Teknolojiler

* Python 3.x
* socket
* threading
* json, mimetypes
* Docker

---
## 🧑‍💻 Geliştiren

* Mert Baytaş
