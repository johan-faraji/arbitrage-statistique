from data_loader import DataLoader
from pairs_finder import PairsFinder
from backtester import Backtester
from visualizer import Visualizer  # N'oublie pas l'import !

if __name__ == "__main__":
    db_name = "finance_data.db"
    
    loader = DataLoader(db_name)
    tickers_test = ["SPY", "IVV", "GOOG", "GOOGL"]
    
    print("--- 1. Ingestion & Analyse ---")
    for ticker in tickers_test:
        loader.save_ticker_metadata(ticker)
        loader.fetch_and_save_prices(ticker, start_date="2021-01-01", end_date="2026-01-01")
        
    finder = PairsFinder(db_name)
    series_goog, series_googl = finder.charge_prices("GOOG", "GOOGL")
    
    print("\n--- 2. Lancement du Backtester (Sprint 3) ---")
    backtester = Backtester(initial_capital=10000.0)
    # On récupère les DEUX variables renvoyées
    equity, z_score = backtester.run(series_goog, series_googl)
    
    print("\n--- 3. Génération des graphiques (Sprint 4) ---")
    Visualizer.plot_results(equity, z_score)