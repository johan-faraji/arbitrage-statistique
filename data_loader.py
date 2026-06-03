import sqlite3
import yfinance as yf
import pandas as pd

class DataLoader:
    def __init__(self, db_name="finance_data.db"):

        self.db_name = db_name
        # On ouvre la connexion UNE SEULE FOIS ici
        self.con = sqlite3.connect(self.db_name)
        self.cursor = self.con.cursor()
        # On crée les tables immédiatement à l'initialisation
        self.create_tables()

    def create_tables(self):

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                ticker TEXT PRIMARY KEY, 
                name TEXT, 
                sector TEXT
            )
        """)
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                ticker TEXT, 
                date TEXT, 
                adj_close REAL, 
                volume INTEGER,
                FOREIGN KEY (ticker) REFERENCES assets(ticker)
            )
        """)
        self.con.commit()

    def save_ticker_metadata(self, ticker):

        asset = yf.Ticker(ticker)
        
        # Sécurité au cas où l'API ne trouve pas le secteur ou le nom
        sector = asset.info.get('sector', 'Unknown')
        name = asset.info.get('longName', ticker)

        # On utilise des '?' pour injecter proprement les variables Python en SQL
        self.cursor.execute(
            "INSERT OR IGNORE INTO assets VALUES (?, ?, ?)", 
            (ticker, name, sector)
        )
        self.con.commit()

    def fetch_and_save_prices(self, ticker, start_date, end_date):
        """
        Cette méthode devra télécharger l'historique des prix via yfinance,
        puis insérer les lignes (date, adj_close, volume) dans la table 'prices'.
        """
        asset = yf.Ticker(ticker)
        data = asset.history(start=start_date, end=end_date)
        data = data[["Close", "Volume"]]
        data = data.rename(columns={"Close": "adj_close"})
        data.index.name = "date"
        data["ticker"] = ticker
        data.to_sql(name='prices', con=self.con, if_exists='append', index=True)


# Ce bloc s'exécute uniquement si on lance ce fichier directement
if __name__ == "__main__":
    
    # 1. On instancie notre loader (ça va créer la DB et les tables automatiquement)
    loader = DataLoader("test_finance.db")
    
    # 2. On choisit un ticker test (ex: TotalEnergies sur la bourse de Paris)
    ticker_test = "TTE.PA"
    
    print(f"Téléchargement des métadonnées pour {ticker_test}...")
    loader.save_ticker_metadata(ticker_test)
    
    print(f"Téléchargement des prix historiques...")
    loader.fetch_and_save_prices(ticker_test, start_date="2025-01-01", end_date="2026-01-01")
    
    print("Félicitations, tout s'est exécuté sans erreur ! Vérifie ton dossier, un fichier 'test_finance.db' a dû apparaître.")