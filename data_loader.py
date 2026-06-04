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
        """
        Crée toutes les tables nécessaires (prices et assets) avec des 
        contraintes d'unicité lors de l'initialisation de la base de données.
        """
        cursor = self.con.cursor()
        
        # 1. Recréation de la table prices (déjà fait)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prices (
                date TEXT,
                ticker TEXT,
                adj_close REAL,
                PRIMARY KEY (date, ticker)
            )
        """)
        
        # 2. AJOUT : Création de la table assets manquante
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS assets (
                ticker TEXT PRIMARY KEY,
                name TEXT,
                sector TEXT
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
        Télécharge les prix depuis yfinance et les sauvegarde sans doublons.
        Gère la nouvelle structure MultiIndex de yfinance.
        """
        print(f"Téléchargement des données pour {ticker}...")
        
        # On ajoute auto_adjust=False pour s'assurer d'avoir la colonne 'Adj Close' 
        # et on demande explicitement de ne pas garder les MultiIndex si possible
        data = yf.download(ticker, start=start_date, end=end_date, auto_adjust=False)
        
        if data.empty:
            print(f"Aucune donnée trouvée pour {ticker}")
            return
            
        # --- SÉCURITÉ MULTIINDEX ---
        # Si yfinance a renvoyé des colonnes à double niveau (ex: ('Adj Close', 'SPY'))
        # on ne garde que le premier niveau (ex: 'Adj Close')
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
            
        df = pd.DataFrame()
        
        # Sécurité supplémentaire au cas où les colonnes sont en minuscules
        if 'Adj Close' in data.columns:
            df['adj_close'] = data['Adj Close']
        elif 'adj_close' in data.columns:
            df['adj_close'] = data['adj_close']
        else:
            # Si vraiment on ne trouve pas la clôture ajustée, on se rabat sur la clôture classique
            df['adj_close'] = data['Close'] if 'Close' in data.columns else data['close']
            
        df['ticker'] = ticker
        df = df.reset_index()
        
        # On standardise le nom de la colonne Date
        df.columns = [col.lower() for col in df.columns] # Tout en minuscules ('date', 'adj_close', 'ticker')
        df['date'] = pd.to_datetime(df['date']).dt.strftime('%Y-%m-%d')
        
        # Transfert sécurisé via la table temporaire
        df.to_sql("temp_prices", con=self.con, if_exists="replace", index=False)
        
        cursor = self.con.cursor()
        cursor.execute("""
            INSERT OR IGNORE INTO prices (date, ticker, adj_close)
            SELECT date, ticker, adj_close FROM temp_prices
        """)
        cursor.execute("DROP TABLE temp_prices")
        self.con.commit()
        print(f"Données de {ticker} sauvegardées avec succès (doublons ignorés).")


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