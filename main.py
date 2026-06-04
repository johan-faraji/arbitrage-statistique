from data_loader import DataLoader
from pairs_finder import PairsFinder

if __name__ == "__main__":
    # --- SPRINT 1 : TELECHARGEMENT ET STOCKAGE ---
    db_name = "finance_data.db"
    loader = DataLoader(db_name)
    
    # Liste de banques et d'énergies françaises pour le test
    tickers_test = ["SPY", "IVV", "GOOG", "GOOGL"]
    
    print("--- Début du Sprint 1 : Ingestion des données ---")
    for ticker in tickers_test:
        print(f"Traitement de {ticker}...")
        loader.save_ticker_metadata(ticker)
        # On prend un historique de 5 ans pour avoir des stats solides
        loader.fetch_and_save_prices(ticker, start_date="2021-01-01", end_date="2026-01-01")
        
    print("\n--- Début du Sprint 2 : Analyse des Paires ---")
    # --- SPRINT 2 : RECHERCHE DE COINTEGRATION ---
    finder = PairsFinder(db_name)
    resultats = finder.find_all_pairs(tickers_test)
    
    print("\n--- Synthèse des résultats ---")
    if len(resultats) == 0:
        print("Aucune paire cointégrée trouvée sur cette période.")
    else:
        print(f"Scan terminé. {len(resultats)} paire(s) exploitable(s) détectée(s).")