import time
from data_loader import DataLoader

loader = DataLoader("finance_data.db")

def calculate_historical_metrics():
    beta = 1.00  # Ajustable selon ton modèle OLS du Sprint 5
    mean, std = loader.get_historical_metrics(beta=beta)
    
    print(f"   -> Moyenne historique (µ) : {mean:.4f}")
    print(f"   -> Écart-type (σ)        : {std:.4f}")
    print(f"   -> Beta utilisé          : {beta:.2f}")
    
    return mean, std, beta

if __name__ == "__main__":
    BETA = 1.00
    WINDOW = 20 # Fenêtre glissante identique au backtest et à app.py
    
    print("🛡️ Surveillance du Z-Score glissant activée. En attente de variations...")
    print("-" * 60)
    
    last_seen_date = None
    
    try:
        while True:
            # 1. On récupère les 100 derniers spreads en base (données récentes récoltées par le feeder)
            recent_spreads = loader.get_recent_spreads(limit=100)
            
            if len(recent_spreads) >= WINDOW:
                # 2. On passe par un DataFrame pour calculer le rolling Z-Score comme sur le dashboard
                df = pd.DataFrame(recent_spreads, columns=["date", "GOOG", "GOOGL"])
                df["Spread"] = df["GOOG"] - (BETA * df["GOOGL"])
                
                rolling_mean = df["Spread"].rolling(window=WINDOW).mean()
                rolling_std = df["Spread"].rolling(window=WINDOW).std()
                df["Z-Score"] = (df["Spread"] - rolling_mean) / rolling_std
                
                # 3. Extraction du tout dernier point (le point actuel)
                current_time = df["date"].iloc[-1]
                price_goog = df["GOOG"].iloc[-1]
                price_googl = df["GOOGL"].iloc[-1]
                z_score = df["Z-Score"].iloc[-1]
                current_spread = df["Spread"].iloc[-1]
                
                # Sécurité si le rolling génère des NaN au démarrage
                if pd.isna(z_score):
                    time.sleep(1)
                    continue
                
                # On ne traite le point que s'il est nouveau
                if current_time != last_seen_date:
                    last_seen_date = current_time
                    
                    open_position = loader.has_open_position()

                    if open_position is None:
                        status = "⚪ NEUTRE"
                        if z_score >= 2.5:
                            status = "🚨 VENDRE GOOG / ACHETER GOOGL (Z HIGH)"
                            signal_type = "SELL_SPREAD"
                            loader.open_trade(current_time, signal_type, price_goog, price_googl, BETA)
                        elif z_score <= -2.5:
                            status = "🚨 ACHETER GOOG / VENDRE GOOGL (Z LOW)"
                            signal_type = "BUY_SPREAD"
                            loader.open_trade(current_time, signal_type, price_goog, price_googl, BETA)
                            
                        print(f"[{current_time}] GOOG: {price_goog:.2f}$ | GOOGL: {price_googl:.2f}$ | Z-Score: {z_score:+.2f} | {status}")

                    else:
                        order_id = open_position[0]
                        signal_type = open_position[3]
                        entry_goog = open_position[5]
                        entry_googl = open_position[6]

                        entry_spread = entry_goog - (BETA * entry_googl)

                        # 🎯 CONDITION DE SORTIE (Désormais parfaitement synchrone avec app.py)
                        if (signal_type == "BUY_SPREAD" and z_score >= 0) or (signal_type == "SELL_SPREAD" and z_score <= 0):
                            print(f"🎯 SIGNAL EXIT: RETOUR À LA MOYENNE DÉTECTÉ (Z-Score: {z_score:+.2f})")
                            
                            if signal_type == "BUY_SPREAD":
                                pnl = current_spread - entry_spread
                            else:
                                pnl = entry_spread - current_spread
                                
                            loader.close_trade(order_id, current_time, price_goog, price_googl, pnl)
                            print(f"✅ Position {order_id} fermée en base avec succès. PnL: {pnl:.2f}$")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de la surveillance.")