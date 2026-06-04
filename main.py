from data_loader import DataLoader
from pairs_finder import PairsFinder
from backtester import Backtester

if __name__ == "__main__":
    db_name = "finance_data.db"
    
    # --- SPRINT 1 & 2 (Déjà fait, on réutilise) ---
    loader = DataLoader(db_name)
    tickers_test = ["SPY", "IVV", "GOOG", "GOOGL"]
    
    print("--- 1. Ingestion & Analyse ---")
    for ticker in tickers_test:
        loader.save_ticker_metadata(ticker)
        loader.fetch_and_save_prices(ticker, start_date="2021-01-01", end_date="2026-01-01")
        
    finder = PairsFinder(db_name)
    # On sait déjà que GOOG et GOOGL fonctionne !
    
    print("\n--- 2. Chargement des données de la paire validée ---")
    # On extrait les séries de prix de notre paire gagnante
    series_goog, series_googl = finder.charge_prices("GOOG", "GOOGL")
    
    print("\n--- 3. Lancement du Backtester (Sprint 3) ---")
    backtester = Backtester(initial_capital=10000.0)
    equity = backtester.run(series_goog, series_googl)