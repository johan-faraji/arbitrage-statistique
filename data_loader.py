import sqlite3
# !!! RETIRE L'IMPORT DE YFINANCE D'ICI !!!

class DataLoader:
    def __init__(self, db_path):
        self.con = sqlite3.connect(db_path)
        # On s'assure que la table existe au cas où
        self.create_tables()

    def create_tables(self):
        query = """
        CREATE TABLE IF NOT EXISTS prices (
            date TEXT,
            ticker TEXT,
            adj_close REAL,
            PRIMARY KEY (date, ticker)
        );
        """
        self.con.cursor().execute(query)
        self.con.commit()

    def download_historical_data(self, tickers, start_date, end_date):
        """Télécharge les données historiques."""
        # TECHNIQUE DU LAZY LOADING : 
        # On n'importe yfinance QUE si cette méthode précise est appelée.
        import yfinance as yf
        
        print(f"📥 Téléchargement historique pour {tickers}...")
        # Laisse le reste de ton code existant pour le téléchargement historique ici...

    def save_live_price(self, date_str, ticker, price):
        """Insère ou met à jour un prix reçu en temps réel dans la table prices."""
        query = "INSERT OR REPLACE INTO prices (date, ticker, adj_close) VALUES (?, ?, ?)"
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (date_str, ticker, price))
            self.con.commit()
        except Exception as e:
            print(f"⚠️ Erreur lors de l'insertion SQLite : {e}")

    def get_latest_price(self, ticker):
        """Récupère le prix le plus récent et sa date pour un ticker donné."""
        query = """
            SELECT date, adj_close 
            FROM prices 
            WHERE ticker = ? 
            ORDER BY date DESC 
            LIMIT 1
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (ticker,))
            return cursor.fetchone()
        except Exception as e:
            print(f"⚠️ Erreur lors de la récupération du dernier prix : {e}")
            return None
        
    def get_historical_metrics(self, beta=1.00):
        """
        Calcule la moyenne et l'écart-type du spread historique (GOOG - beta * GOOGL)
        uniquement à partir des données quotidiennes (timestamps courts sans heures).
        """
        # On filtre sur les dates historiques (ex: format 'YYYY-MM-DD' de yfinance)
        # pour ne pas mélanger les données intraday (qui ont des millisecondes)
        query = """
            SELECT 
                g.date,
                (g.adj_close - (? * gl.adj_close)) as spread
            FROM prices g
            JOIN prices gl ON g.date = gl.date
            WHERE g.ticker = 'GOOG' 
            AND gl.ticker = 'GOOGL'
            AND length(g.date) <= 10  -- Filtre pour ne prendre que le format '2026-05-17'
        """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (beta,))
            rows = cursor.fetchall()
            
            if not rows:
                print("⚠️ Aucune donnée historique trouvée pour calculer les métriques.")
                return 0.0, 1.0
            
            # Extraction des spreads
            spreads = [row[1] for row in rows]
            n = len(spreads)
            
            # Calcul de la moyenne (µ)
            mean = sum(spreads) / n
            
            # Calcul de l'écart-type (σ)
            variance = sum((x - mean) ** 2 for x in spreads) / (n - 1) if n > 1 else 1.0
            std = variance ** 0.5
            
            print(f"📊 Métriques historiques calculées sur {n} jours de specs.")
            return mean, std
            
        except Exception as e:
            print(f"⚠️ Erreur lors du calcul statistique SQL : {e}")
            return 0.0, 1.0