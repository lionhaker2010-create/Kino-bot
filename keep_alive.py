from flask import Flask
import os
import time
import requests
from threading import Thread

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

def run_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        print(f"🚀 Starting server on port {port}...")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Server error: {e}")

def keep_alive():
    server_thread = Thread(target=run_server, daemon=True)
    server_thread.start()
    print("✅ Keep-alive server started!")

def start_pinging():
    print("🔄 Auto-ping service started!")
    
    render_url = 'https://kino-bot-08ke.onrender.com'
    
    while True:
        try:
            requests.get(f"{render_url}/", timeout=5)
            requests.get(f"{render_url}/health", timeout=5)
            print(f"🔄 Ping sent - {time.strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"❌ Ping failed: {e}")
        
        time.sleep(600)  # 10 daqiqa

def start_background_ping():
    ping_thread = Thread(target=start_pinging, daemon=True)
    ping_thread.start()