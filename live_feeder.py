import websocket
import json
import pandas as pd
from data_loader import DataLoader

# On initialise notre DataLoader (il a déjà notre sécurité anti-doublons !)
loader = DataLoader("finance_data.db")
API_KEY = "d8h8vuhr01qhjpmr51igd8h8vuhr01qhjpmr51j0"

def on_message(ws, message):
    """
    Cette fonction est appelée AUTOMATIQUEMENT à chaque fois 
    que Finnhub envoie un nouveau prix.
    """
    json_data = json.loads(message)
    
    # Sécurité : On vérifie si le message contient bien des données de trade
    if json_data.get("type") == "trade":
        trades = json_data["data"]
        for trade in trades:
            ticker = trade["s"]
            price = trade["p"]
            timestamp = trade["t"]
            
            # --- À TOI DE JOUER ---
            # 1. Convertis le timestamp (en ms) en une date lisible au format 'Y-m-d H:M:S'
            #    Astuce : pd.to_datetime(timestamp, unit='ms').strftime('%Y-%m-%d %H:%M:%S')
            date = pd.to_datetime(timestamp, unit='ms').strftime('%Y-%m-%d %H:%M:%S')
            
            # 2. Prépare un mini-DataFrame ou appelle directement une méthode SQL 
            #    pour insérer (date, ticker, price) dans ta table 'prices'.
            loader.save_live_price(date, ticker, price)
            # 3. Ajoute un petit print pour voir le prix défiler dans ton terminal.
            print(f"{ticker} : {price} $ à {date}")

def on_open(ws):
    """Fonction appelée dès que la connexion est établie : on s'abonne aux actifs."""
    print("🚀 Connexion WebSocket établie avec Finnhub !")
    # On s'abonne à Google (Classe C)
    #ws.send(json.dumps({"type": "subscribe", "symbol": "GOOG"}))
    # On s'abonne à Google (Classe A)
    #ws.send(json.dumps({"type": "subscribe", "symbol": "GOOGL"}))
    ws.send(json.dumps({"type": "subscribe", "symbol": "BINANCE:BTCUSDT"}))

if __name__ == "__main__":
    # Connexion à l'URL de Finnhub avec ta clé API
    ws_url = f"wss://ws.finnhub.io?token={API_KEY}"
    ws = websocket.WebSocketApp(ws_url, on_message=on_message, on_open=on_open)
    
    print("Démarrage du Feeder Live... (Appuie sur Ctrl+C pour arrêter)")
    ws.run_forever()