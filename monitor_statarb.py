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
                    
                    status = "⚪ NEUTRE"
                    if z_score >= 2.0:
                        status = "🚨 VENDRE GOOG / ACHETER GOOGL (Z HIGH)"
                    elif z_score <= -2.0:
                        status = "🚨 ACHETER GOOG / VENDRE GOOGL (Z LOW)"
                        
                    print(f"[{current_time}] GOOG: {price_goog:.2f}$ | GOOGL: {price_googl:.2f}$ | Spread: {current_spread:.2f} | Z-Score: {z_score:+.2f} | {status}")
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Arrêt de la surveillance.")