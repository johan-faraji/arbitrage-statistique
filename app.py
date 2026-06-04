import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
from backtester import Backtester
from pairs_finder import PairsFinder

# Configuration de la page Streamlit
st.set_page_config(page_title="Quant Dashboard - StatArb", layout="wide")

st.title("📈 Moteur d'arbitrage statistique en temps réel")
st.markdown("Bienvenue sur ton dashboard de trading quantitatif.")

# --- CHARGEMENT DES DONNÉES ---
db_name = "finance_data.db"

# Petit bouton dans la barre latérale pour rafraîchir
if st.sidebar.button("Calculer le backtest"):
    finder = PairsFinder(db_name)
    series_goog, series_googl = finder.charge_prices("GOOG", "GOOGL")
    
    backtester = Backtester(initial_capital=10000.0)
    # On récupère désormais les 3 variables
    equity, z_score, global_returns = backtester.run(series_goog, series_googl)
    
    # --- AFFICHAGE DES METRIQUES EN HAUT ---
    col1, col2, col3 = st.columns(3)
    
    final_cap = equity.iloc[-1]
    ret = ((final_cap - 10000.0) / 10000.0) * 100
    mdd = backtester.calculate_max_drawdown(equity)
    # On passe les bons rendements ici !
    sharpe = backtester.calculate_sharpe_ratio(global_returns)
    
    col1.metric(label="Rendement total", value=f"{ret:.2f} %")
    col2.metric(label="Max Drawdown (Risque)", value=f"{mdd:.2f} %")
    col3.metric(label="Ratio de Sharpe", value=f"{sharpe:.2f}")
    
    # --- GRAPHIQUE INTERACTIF ---
    st.subheader("Évolution du capital (Equity Curve)")
    st.line_chart(equity)
else:
    st.info("Clique sur 'Calculer le backtest' dans la barre latérale pour lancer l'analyse.")