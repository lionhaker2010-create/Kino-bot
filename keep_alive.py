# keep_alive.py
from flask import Flask
from threading import Thread
import time
import requests
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Kino Bot is running! ✅"

@app.route('/health')
def health():
    return "🟢 OK"

@app.route('/ping')
def ping():
    return "pong"

def run():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

def keep_alive():
    server = Thread(target=run)
    server.start()

# 🔥 YANGILANGAN PING FUNKSIYASI
def start_pinging():
    print("🔄 Auto-ping service started!")
    
    render_url = 'https://kino-bot-08ke.onrender.com'
    
    while True:
        try:
            # Har 10 daqiqada ping
            requests.get(f"{render_url}/", timeout=5)
            requests.get(f"{render_url}/health", timeout=5)
            print(f"🔄 Ping sent - {time.strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"❌ Ping failed: {e}")
        
        time.sleep(600)  # 10 daqiqa

# Background da ishlash uchun
def start_background_ping():
    ping_thread = Thread(target=start_pinging, daemon=True)
    ping_thread.start()