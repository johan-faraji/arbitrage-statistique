import sqlite3
import pandas as pd
import yfinance as yf

DB_NAME = "finance_data.db"
TICKERS = ["GOOG", "GOOGL"]
START_DATE = "2021-01-01"
END_DATE = "2026-06-01"

def seed_historical_database():
    con = sqlite3.connect(DB_NAME)
    cursor = con.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS historical_prices (
        date TEXT,
        ticker TEXT,
        adj_close REAL,
        PRIMARY KEY (date, ticker)
    );
    """)
    con.commit()
    
    print("Début de la récolte locale de l'historique...")
    
    try:
        for ticker in TICKERS:
            print(f"Téléchargement des données pour {ticker}...")
            
            data = yf.download(ticker, start=START_DATE, end=END_DATE, group_by="ticker")
            
            if data.empty:
                print(f"Aucun cours trouvé pour {ticker}")
                continue
            
            # Si yfinance a créé un MultiIndex (ex: [('GOOG', 'Close'), ...]), on nettoie
            if isinstance(data.columns, pd.MultiIndex):
                # On ne garde que le deuxième niveau (Open, High, Low, Close, etc.)
                data.columns = data.columns.get_level_values(-1)
                
            count = 0
            for timestamp, row in data.iterrows():
                date_str = timestamp.strftime('%Y-%m-%d')
                
                # Extraction sécurisée du prix de clôture
                if 'Adj Close' in row and not pd.isna(row['Adj Close']):
                    close_val = float(row['Adj Close'])
                else:
                    close_val = float(row['Close'])
                
                # Insertion ciblée dans la table historique
                query = "INSERT OR REPLACE INTO historical_prices (date, ticker, adj_close) VALUES (?, ?, ?)"
                cursor.execute(query, (date_str, ticker, close_val))
                count += 1
                
            con.commit()
            print(f"{count} lignes insérées avec succès pour {ticker} dans 'historical_prices'.")
            
        print("\nBase de données locale pré-remplie avec succès ! Le fichier 'finance_data.db' est prêt.")
        
    except Exception as e:
        print(f"Erreur lors de la récolte locale : {e}")
    finally:
        con.close()

if __name__ == "__main__":
    seed_historical_database()
