import sqlite3

class DataLoader:
    def __init__(self, db_path):
        self.con = sqlite3.connect(db_path)
        # On s'assure que la table existe au cas où
        self.create_tables()
        self.create_orders_table()

    def create_tables(self):
        query_live = """
        CREATE TABLE IF NOT EXISTS prices (
            date TEXT,
            ticker TEXT,
            adj_close REAL,
            PRIMARY KEY (date, ticker)
        );
        """

        query_hist = """
        CREATE TABLE IF NOT EXISTS historical_prices (
            date TEXT,
            ticker TEXT,
            adj_close REAL,
            PRIMARY KEY (date, ticker)
        );
        """
        self.con.cursor().execute(query_live)
        self.con.cursor().execute(query_hist)
        self.con.commit()

    def create_orders_table(self):
        query = """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date_entry TEXT,
            date_exit TEXT,
            signal_type TEXT,
            status TEXT,
            entry_goog REAL,
            entry_googl REAL,
            exit_goog REAL,
            exit_googl REAL,
            beta REAL,
            pnl REAL
            )
        """
        self.con.cursor().execute(query)
        self.con.commit()

    def download_historical_data(self, tickers, start_date, end_date):
        """Télécharge les données historiques et les stocke dans historical_prices."""
        import yfinance as yf
        import requests
        
        try:
            session = requests.Session()
            session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            })
            
            for ticker in tickers:
                print(f"Téléchargement historique pour {ticker}...")
                ticker_obj = yf.Ticker(ticker, session=session)
                data = ticker_obj.history(start=start_date, end=end_date)
                
                if data.empty:
                    print(f"Aucun cours trouvé pour {ticker}")
                    continue
                
                cursor = self.con.cursor()
                for timestamp, row in data.iterrows():
                    date_str = timestamp.strftime('%Y-%m-%d')
                    close_val = float(row['Close'])
                    
                    # INSERTION DANS HISTORICAL_PRICES
                    query = "INSERT OR REPLACE INTO historical_prices (date, ticker, adj_close) VALUES (?, ?, ?)"
                    cursor.execute(query, (date_str, ticker, close_val))
                
                self.con.commit()
            return True
        except Exception as e:
            print(f"Erreur lors du téléchargement historique : {e}")
            return False

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
                print("Aucune donnée historique trouvée pour calculer les métriques.")
                return 0.0, 1.0
            
            # Extraction des spreads
            spreads = [row[1] for row in rows]
            n = len(spreads)
            
            # Calcul de la moyenne (µ)
            mean = sum(spreads) / n
            
            # Calcul de l'écart-type (σ)
            variance = sum((x - mean) ** 2 for x in spreads) / (n - 1) if n > 1 else 1.0
            std = variance ** 0.5
            
            print(f"Métriques historiques calculées sur {n} jours de specs.")
            return mean, std
            
        except Exception as e:
            print(f"Erreur lors du calcul statistique SQL : {e}")
            return 0.0, 1.0
        
    def has_open_position(self):
        query = """
        SELECT * FROM orders WHERE status = 'OPEN'
        """

        cursor = self.con.cursor()
        cursor.execute(query)
        row = cursor.fetchone()
        
        if not row:
            return None
        
        return row
    
    def open_trade(self, date_entry, signal_type, entry_goog, entry_googl, beta):
        
        query = "INSERT INTO orders (date_entry, signal_type, status, entry_goog, entry_googl, beta) VALUES (?, ?, ?, ?, ?, ?)"
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (date_entry, signal_type, 'OPEN', entry_goog, entry_googl, beta))
            self.con.commit()
        except Exception as e:
            print(f"Erreur lors de l'insertion SQLite : {e}")
        

    def close_trade(self, order_id, date_exit, exit_goog, exit_googl, pnl):
        """
        Clôture une position existante via son order_id (status='CLOSED').
        """
        query = """
            UPDATE orders SET 
            status = 'CLOSED',
            date_exit = ?,
            exit_goog = ?,
            exit_googl = ?,
            pnl = ?
            WHERE id = ?
            """
        try:
            cursor = self.con.cursor()
            cursor.execute(query, (date_exit, exit_goog, exit_googl, pnl, order_id))
            self.con.commit()
        except Exception as e:
            print(f"Erreur lors de la MAJ de la table SQLite : {e}")

    def get_recent_spreads(self, limit=100):
        query = """
                SELECT 
                    g.date, 
                    g.adj_close AS price_goog, 
                    gl.adj_close AS price_googl
                FROM prices g
                JOIN prices gl ON g.date = gl.date
                WHERE g.ticker = 'GOOG' AND gl.ticker = 'GOOGL'
                ORDER BY g.date DESC
                LIMIT ?
                """
        cursor = self.con.cursor()
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        return rows[::-1]
    
    def get_all_orders(self) :
        query = """SELECT * FROM orders"""
        cursor = self.con.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        return rows
    
    def reset_orders_table(self):
        """Vide proprement la table des ordres pour recommencer une session de test à zéro."""
        query = "DELETE FROM orders;"
        try:
            cursor = self.con.cursor()
            cursor.execute(query)
            self.con.commit()
            print("Table des ordres vidée avec succès pour la nouvelle session.")
        except Exception as e:
            print(f"Erreur lors du nettoyage de la table orders : {e}")
