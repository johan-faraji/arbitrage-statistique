import sqlite3
import pandas as pd
from statsmodels.tsa.stattools import coint
from itertools import combinations

class PairsFinder :
    def __init__(self, db_name="finance_data.db"):
        self.db_name = db_name
        # On crée une connexion propre dédiée à la lecture des données
        self.con = sqlite3.connect(self.db_name)

    def charge_prices(self, ticker1, ticker2):

        query = "SELECT date, adj_close FROM historical_prices WHERE ticker = ? ORDER BY date"

        df1 = pd.read_sql_query(query, self.con, params=(ticker1,))
        df1 = df1.rename(columns={"adj_close": ticker1})

        df2 = pd.read_sql_query(query, self.con, params=(ticker2,))
        df2 = df2.rename(columns={"adj_close": ticker2})

        df_final = pd.merge(df1, df2, on="date", how="inner")
        df_final = df_final.set_index("date")

        return df_final[ticker1], df_final[ticker2]
    
    @staticmethod
    def test_cointegration(series1, series2):
        res = coint(series1, series2)
        return res[1]
    
    def find_all_pairs(self, tickers_list):
        # 1. On génère toutes les paires uniques possibles
        all_pairs = list(combinations(tickers_list, 2))
        print(f"Nombre de paires à tester : {len(all_pairs)}")

        pairs_valides = []

        for ticker1, ticker2 in all_pairs:
            try:
                # 2. On charge les prix alignés
                s1, s2 = self.charge_prices(ticker1, ticker2)
                
                # Sécurité : Si on n'a pas assez de données communes, on passe à la suite
                if len(s1) < 100: 
                    continue
                    
                # 3. On calcule la p-value
                p_value = self.test_cointegration(s1, s2)
                
                # 4. Si la p-value est bonne, on garde la paire
                if p_value < 0.05:
                    print(f"Paire trouvée ! {ticker1} et {ticker2} (p-value: {p_value:.4f})")
                    pairs_valides.append((ticker1, ticker2, p_value))
                    
            except Exception as e:
                # Si un ticker bugge ou n'a pas de données, on ne bloque pas tout le script
                print(f"Erreur sur la paire {ticker1}-{ticker2}: {e}")
                continue
                
        return pairs_valides
