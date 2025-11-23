from flask import Flask
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

# FAQAT BITTA SERVER ISHGA TUSHIRISH
def run_server():
    try:
        port = int(os.environ.get("PORT", 10000))
        print(f"🚀 Starting server on port {port}...")
        app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"❌ Server error: {e}")

def keep_alive():
    import threading
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    print("✅ Keep-alive server started!")