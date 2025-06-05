#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Bu satır, kodun gerçekten çalışıp çalışmadığını anlamak için ilk andaki durumu gösterir:
print(">>> server.py başladı <<<", flush=True)

import socket
import threading
import os
import json
import mimetypes
import sys
import io
from datetime import datetime

# ------------------------------------------------------
# Windows’ta Türkçe karakter veya emoji basmak için UTF-8 çıktısını zorlarız
# ------------------------------------------------------
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# -----------------------------
# KONFIGÜRASYON
# -----------------------------
HOST = '0.0.0.0'
PORT = 81
STATIC_DIR = './static'       # Statik dosyalar (HTML, CSS, JS, resim) burada
TEMPLATE_DIR = './templates'  # Basit template engine için HTML şablonları
LOG_FILE = 'server.log'       # İstek loglarının yazılacağı dosya

# -----------------------------
# ROUTE HANDLER REGİSTRASYONU
# -----------------------------
# Key: (path, method), Value: handler fonksiyonu
routes = {}

def route(path, method='GET'):
    """
    @route('/api/hello', method='GET') şeklinde kullanılır.
    Bu decorator, handler’ı routes sözlüğüne ekler.
    """
    def decorator(func):
        routes[(path, method.upper())] = func
        return func
    return decorator

# -----------------------------
# LOG FONKSİYONU (Thread-safe)
# -----------------------------
log_lock = threading.Lock()

def log_request(method, ip, path, response_code):
    """
    Her istek alındığında server.log içine tek satır yazar:
    "tarih - ip - METHOD PATH -> STATUS"
    """
    entry = f"{datetime.now().isoformat()} - {ip} - {method} {path} -> {response_code}\n"
    with log_lock:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(entry)

# -----------------------------
# BASİT TEMPLATE ENGINE
# -----------------------------
def render_template(template_name, context=None):
    """
    ./templates klasöründen template_name dosyasını okur.
    İçindeki {{key}} yer tutucuları context['key'] değerleriyle değiştirir.
    """
    context = context or {}
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    if not os.path.isfile(template_path):
        raise FileNotFoundError(f"Template {template_name} bulunamadı.")
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()
    # Her {{key}} yer tutucusunu context[key] ile değiştirir
    for key, value in context.items():
        placeholder = '{{' + key + '}}'
        content = content.replace(placeholder, str(value))
    return content.encode('utf-8')

# -----------------------------
# STATİK DOSYA SERVİSİ
# -----------------------------
def serve_static_file(relative_path):
    """
    /static/... yolu ile erişilen dosyaları sunar.
    Dosya varsa içerik ve doğru MIME tipini döner. Yoksa 404 verir.
    """
    local_path = os.path.join(STATIC_DIR, relative_path.lstrip('/'))
    if os.path.isfile(local_path):
        with open(local_path, 'rb') as f:
            content = f.read()
        mime_type = mimetypes.guess_type(local_path)[0] or 'application/octet-stream'
        headers = (
            "HTTP/1.1 200 OK\r\n"
            f"Content-Type: {mime_type}\r\n"
            f"Content-Length: {len(content)}\r\n"
            "\r\n"
        ).encode('utf-8')
        return headers + content, 200
    else:
        return (
            b"HTTP/1.1 404 Not Found\r\n"
            b"Content-Type: text/plain\r\n"
            b"\r\n"
            b"File Not Found"
        ), 404

# -----------------------------
# ROUTE HANDLER ÖRNEKLERİ
# -----------------------------

@route('/api/hello', method='GET')
def hello_handler(_):
    """
    GET /api/hello → JSON: {"message": "Hello, world!"}
    """
    body = json.dumps({'message': 'Hello, world!'}).encode('utf-8')
    headers = (
        "HTTP/1.1 200 OK\r\n"
        "Content-Type: application/json\r\n"
        f"Content-Length: {len(body)}\r\n"
        "\r\n"
    ).encode('utf-8')
    return headers + body, 200

@route('/api/greet', method='POST')
def greet_handler(body_bytes):
    """
    POST /api/greet 
    Beklenen JSON gövde: {"name": "...", "surname": "..."}
    Döner: {"message": "Selam name surname"}
    """
    try:
        body_str = body_bytes.decode('utf-8')
        data = json.loads(body_str)
        name = data.get('name', '').strip()
        surname = data.get('surname', '').strip()
        if not name:
            raise ValueError("name alanı gerekli.")
        message = f"Selam {name} {surname}".strip()
        response_body = json.dumps({'message': message}).encode('utf-8')
        headers = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: application/json\r\n"
            f"Content-Length: {len(response_body)}\r\n"
            "\r\n"
        ).encode('utf-8')
        return headers + response_body, 200
    except (json.JSONDecodeError, ValueError) as ve:
        error_msg = str(ve).encode('utf-8')
        headers = (
            "HTTP/1.1 400 Bad Request\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(error_msg)}\r\n"
            "\r\n"
        ).encode('utf-8')
        return headers + error_msg, 400
    except Exception as e:
        error_msg = f"Internal Server Error: {e}".encode('utf-8')
        headers = (
            "HTTP/1.1 500 Internal Server Error\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(error_msg)}\r\n"
            "\r\n"
        ).encode('utf-8')
        return headers + error_msg, 500

@route('/', method='GET')
def index_handler(_):
    """
    GET / → templates/index.html dosyasını render eder.
    """
    try:
        context = {
            'title': 'Ana Sayfa',
            'content': 'Bu, basit HTTP sunucunuzun ana sayfasıdır.'
        }
        rendered = render_template('index.html', context)
        headers = (
            "HTTP/1.1 200 OK\r\n"
            "Content-Type: text/html; charset=utf-8\r\n"
            f"Content-Length: {len(rendered)}\r\n"
            "\r\n"
        ).encode('utf-8')
        return headers + rendered, 200
    except FileNotFoundError:
        return (
            b"HTTP/1.1 404 Not Found\r\n"
            b"Content-Type: text/plain\r\n"
            b"\r\n"
            b"Template Not Found"
        ), 404

# -----------------------------
# İSTEK PARSING (Ayrıştırma)
# -----------------------------
def parse_request(request_data):
    """
    request_data: TCP socket’ten gelen tam HTTP isteğinin string hali.
    Döner: method, path, headers_dict, body (bytes)
    """
    lines = request_data.split('\r\n')
    request_line = lines[0]
    method, path, _ = request_line.split()
    headers = {}
    body = b''
    sep = request_data.find('\r\n\r\n')
    if sep != -1:
        header_lines = lines[1:lines.index('')]
        for h in header_lines:
            if ': ' in h:
                k, v = h.split(': ', 1)
                headers[k.lower()] = v
        body_raw = request_data[sep+4:]
        body = body_raw.encode('utf-8', errors='ignore')
    return method, path, headers, body

# -----------------------------
# İSTEK YÖNLENDİRME VE SERVİS
# -----------------------------
def handle_client(conn, addr):
    ip = addr[0]
    try:
        data = conn.recv(8192).decode('utf-8', errors='ignore')
        if not data:
            conn.close()
            return

        method, path, headers, body = parse_request(data)

        # 1) Statik dosya isteği mi?
        if method == 'GET' and path.startswith('/static/'):
            response, status = serve_static_file(path[len('/static/'):])

        # 2) Kayıtlı route handler var mı?
        elif (path, method) in routes:
            handler = routes[(path, method)]
            response, status = handler(body)

        # 3) Hiçbiri değilse 404
        else:
            response = (
                b"HTTP/1.1 404 Not Found\r\n"
                b"Content-Type: text/plain\r\n"
                b"\r\n"
                b"Not Found"
            )
            status = 404

        # İstek kaydını hem dosyaya hem konsola yaz
        log_request(method, ip, path, status)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {ip} - {method} {path} -> {status}")

        # Yanıtı istemciye gönder
        conn.sendall(response)

    except Exception as e:
        # 500 Internal Server Error durumunda
        error_message = f"Internal Server Error: {e}"
        response = (
            "HTTP/1.1 500 Internal Server Error\r\n"
            "Content-Type: text/plain\r\n"
            f"Content-Length: {len(error_message)}\r\n"
            "\r\n" + error_message
        ).encode('utf-8')
        log_request("ERROR", ip, path if 'path' in locals() else "UNKNOWN", 500)
        print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {ip} - ERROR {path if 'path' in locals() else 'UNKNOWN'} -> 500: {e}")
        conn.sendall(response)

    finally:
        conn.close()

# -----------------------------
# SUNUCU BAŞLATMA
# -----------------------------
def start_server():
    """
    1) Log dosyasını temizler (boşaltır).
    2) Tek bir socket açar; bind, listen yapar.
    3) Başarılı olursa bir kez ”Sunucu çalışıyor” mesajı basar.
    4) Sonsuz döngüde accept() ile gelen her yeni bağlantı için
       ayrı bir thread açarak handle_client(conn, addr) çağırır.
    """
    # 1) Log dosyasını sıfırla (boşalt)
    open(LOG_FILE, 'w').close()

    # 2) Socket’i oluştur, bind ve listen uygula
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            server.bind((HOST, PORT))
        except Exception as bind_err:
            print(">>> Port bind hatası:", bind_err)
            return
        try:
            server.listen(5)
        except Exception as listen_err:
            print(">>> Listen hatası:", listen_err)
            return

        # 3) Başarıyla dinlemeye başladı mesajı
        print(f"Sunucu http://{HOST}:{PORT} adresinde çalışıyor...", flush=True)

        # 4) Ana döngü: her yeni bağlantı için ayrı thread
        while True:
            conn, addr = server.accept()
            print(f"Yeni bağlantı kabul edildi: {addr}")
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

# Program doğrudan çalıştırıldığında start_server() çağrılır
if __name__ == "__main__":
    start_server()
