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
    mean, std, beta = calculate_historical_metrics()
    print("🛡️ Surveillance du Z-Score activée. En attente de variations...")
    print("-" * 60)
    
    last_seen_date = None
    
    try:
        while True:
            goog_data = loader.get_latest_price("GOOG")
            googl_data = loader.get_latest_price("GOOGL")
            
            if goog_data and googl_data:
                date_goog, price_goog = goog_data
                date_googl, price_googl = googl_data
                
                current_time = max(date_goog, date_googl)
                
                if current_time != last_seen_date:
                    last_seen_date = current_time
                    
                    current_spread = price_goog - (beta * price_googl)
                    z_score = (current_spread - mean) / std
                    
                    open_position = loader.has_open_position()

                    if open_position is None :

                        status = "⚪ NEUTRE"
                        if z_score >= 2.5:
                            status = "🚨 VENDRE GOOG / ACHETER GOOGL (Z HIGH)"
                            signal_type = "SELL_SPREAD"
                            loader.open_trade(current_time, signal_type, price_goog, price_googl, beta)
                        elif z_score <= -2.5:
                            status = "🚨 ACHETER GOOG / VENDRE GOOGL (Z LOW)"
                            signal_type = "BUY_SPREAD"
                            loader.open_trade(current_time, signal_type, price_goog, price_googl, beta)
                            
                        print(f"[{current_time}] GOOG: {price_goog:.2f}$ | GOOGL: {price_googl:.2f}$ | Spread: {current_spread:.2f} | Z-Score: {z_score:+.2f} | {status}")

                    else :
                        
                        order_id = open_position[0]
                        signal_type = open_position[3]
                        entry_goog = open_position[5]
                        entry_googl = open_position[6]

                        # Calcule le spread d'entrée pour pouvoir calculer le PnL plus tard
                        entry_spread = entry_goog - (beta * entry_googl)

                        if (signal_type == "BUY_SPREAD" and z_score >= 0) or (signal_type == "SELL_SPREAD" and z_score <= 0):
                            
                            print("🎯 SIGNAL EXIT: RETOUR À LA MOYENNE")
                            exit_spread = price_goog - (beta * price_googl)

                            if signal_type == "BUY_SPREAD" :
                                pnl = exit_spread - entry_spread
                            else :
                                pnl = entry_spread - exit_spread

                                
                            loader.close_trade(order_id, current_time, price_goog, price_googl, pnl)
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de la surveillance.")