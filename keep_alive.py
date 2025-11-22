# keep_alive.py
from flask import Flask
from threading import Thread
import time
import requests
import os

app = Flask('')

@app.route('/')
def home():
    return "🤖 Kino Bot is running! ✅"

@app.route('/ping')
def ping():
    return "pong"

@app.route('/health')
def health():
    return "🟢 Bot is healthy and running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    server = Thread(target=run)
    server.start()

# Ping funksiyasi - botni uyg'otib turadi
def ping_self():
    try:
        # Render URL ni oling (environment dan yoki to'g'ridan-to'g'ri)
        render_url = os.environ.get('RENDER_URL', 'https://your-bot-name.onrender.com')
        response = requests.get(f"{render_url}/health", timeout=10)
        print(f"🔄 Ping sent - Status: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Ping failed: {e}")

# Har 5 daqiqada ping yuborish
def start_pinging():
    print("🔄 Auto-ping service started!")
    while True:
        ping_self()
        time.sleep(300)  # 5 daqiqa