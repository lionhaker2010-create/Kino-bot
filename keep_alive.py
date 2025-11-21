from flask import Flask
from threading import Thread
import time

app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/ping')
def ping():
    return "pong"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    
    # Background ping
    def background_ping():
        while True:
            try:
                # Self-ping every 5 minutes
                import requests
                requests.get("https://kino-bot-l3nw.onrender.com/ping")
            except:
                pass
            time.sleep(300)  # 5 minutes
    
    ping_thread = Thread(target=background_ping)
    ping_thread.daemon = True
    ping_thread.start()