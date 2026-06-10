import json
import ssl
import websocket
import os
import pandas as pd
from dotenv import load_dotenv
from data_loader import DataLoader

# 1. Chargement propre et sécurisé de la clé API
load_dotenv()
API_KEY = os.getenv("FINNHUB_API_KEY")

if not API_KEY:
    print("❌ Erreur : Impossible de trouver FINNHUB_API_KEY dans le fichier .env")
    exit(1)

# 2. Initialisation du DataLoader pour SQLite
loader = DataLoader("finance_data.db")

def on_message(ws, message):
    data = json.loads(message)
    if data.get("type") == "trade":
        for trade in data["data"]:
            ticker = trade["s"]
            price = trade["p"]
            timestamp = trade["t"]
            
            # 🎯 CORRECTION : On s'arrête aux secondes (%S), on vire les millisecondes
            date_lisible = pd.to_datetime(timestamp, unit='ms').strftime('%Y-%m-%d %H:%M:%S')
            
            print(f"⚡ Live Trade | {ticker} : {price} $ | {date_lisible}")
            
            # Sauvegarde en base de données (SQLite gérera l'écrasement ou l'insertion)
            loader.save_live_price(date_lisible, ticker, price)

def on_error(ws, error):
    print(f"⚠️ Erreur WebSocket : {error}")

def on_close(ws, close_status_code, close_msg):
    print("🔌 Connexion WebSocket fermée.")

def on_open(ws):
    print("🚀 Connexion établie ! Abonnement aux flux GOOG et GOOGL...")
    ws.send(f'{{"type":"subscribe","symbol":"GOOG"}}')
    ws.send(f'{{"type":"subscribe","symbol":"GOOGL"}}')

if __name__ == "__main__":

    loader.reset_orders_table()
    
    websocket.enableTrace(False)
    ws = websocket.WebSocketApp(
        f"wss://ws.finnhub.io?token={API_KEY}",
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.on_open = on_open
    ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})