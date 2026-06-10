import streamlit as st
import sqlite3
import pandas as pd
import numpy as np
import time
from backtester import Backtester
from pairs_finder import PairsFinder
from data_loader import DataLoader

# Configuration de la page Streamlit
st.set_page_config(page_title="Quant dashboard - StatArb", layout="wide")

st.title("Plateforme d'arbitrage statistique")

loader = DataLoader("finance_data.db")
db_name = "finance_data.db"
BETA = 1.00

# --- CRÉATION DES ONGLETS ---
tab_live, tab_backtest = st.tabs(["Trading temps réel", "Backtest historique"])

# ==========================================
# ONGLET 1 : BACKTEST HISTORIQUE (Fixé avec session_state)
# ==========================================
with tab_backtest:
    st.header("Analyse rétrospective")
    
    # ==========================================
    # BARRE LATÉRALE : CONFIGURATION & INGESTION
    # ==========================================
    st.sidebar.header("⚙️ Configuration Globale")

    # Section dédiée à la récolte de données
    st.sidebar.subheader("Données historiques")
    if st.sidebar.button("📥 Récolter l'historique (2021-2026)"):
        with st.sidebar.spinner("Téléchargement des cours depuis Yahoo Finance..."):
            # Téléchargement pour notre paire de tickers de référence
            success = loader.download_historical_data(["GOOG", "GOOGL"], "2021-01-01", "2026-06-01")
            
            if success:
                st.sidebar.success("🎉 Historique stocké avec succès dans 'prices' !")
                time.sleep(1.5)
                st.rerun()
            else:
                st.sidebar.error("❌ Échec de la récolte. Regarde les logs de Render.")

    st.sidebar.markdown("---")
    
    st.sidebar.subheader("Analyses")
    if st.sidebar.button("Calculer le backtest"):
        with st.spinner("Calcul du backtest en cours..."):
            finder = PairsFinder(db_name)
            series_goog, series_googl = finder.charge_prices("GOOG", "GOOGL")
            
            if series_goog.empty or series_googl.empty:
                st.error("❌ Impossible de lancer le backtest : l'historique des prix est vide dans la base SQLite de Render. Lance un chargement de données d'abord.")
            else:
                backtester = Backtester(initial_capital=10000.0)
                equity, z_score, global_returns = backtester.run(series_goog, series_googl)
                
                final_cap = equity.iloc[-1]
                ret = ((final_cap - 10000.0) / 10000.0) * 100
                mdd = backtester.calculate_max_drawdown(equity)
                sharpe = backtester.calculate_sharpe_ratio(global_returns)
                
                # Sauvegarde des résultats pour survivre au st.rerun()
                st.session_state["backtest_calculé"] = True
                st.session_state["ret"] = ret
                st.session_state["mdd"] = mdd
                st.session_state["sharpe"] = sharpe
                st.session_state["equity"] = equity

    # 2. Si le backtest est en mémoire, on l'affiche (il ne disparaîtra plus !)
    if st.session_state.get("backtest_calculé", False):
        col1, col2, col3 = st.columns(3)
        col1.metric(label="Rendement total", value=f"{st.session_state['ret']:.2f} %")
        col2.metric(label="Max Drawdown (Risque)", value=f"{st.session_state['mdd']:.2f} %")
        col3.metric(label="Ratio de Sharpe", value=f"{st.session_state['sharpe']:.2f}")
        
        st.subheader("Évolution du capital (Equity Curve)")
        st.line_chart(st.session_state["equity"])
    else:
        st.info("Clique sur 'Calculer le backtest' dans la barre latérale pour lancer l'analyse.")

# ==========================================
# ONGLET 2 : TRADING TEMPS RÉEL (Z-Score Glissant Synchronisé)
# ==========================================
with tab_live:
    st.header("Surveillance des flux en direct")
    
    # 1. Récupération des 100 derniers points (intraday / live)
    recent_spreads = loader.get_recent_spreads(limit=100)
    all_orders = loader.get_all_orders()
    
    if recent_spreads:
        # 2. Mise en DataFrame immédiate pour utiliser la puissance de Pandas
        df_chart = pd.DataFrame(recent_spreads, columns=["date", "GOOG", "GOOGL"])
        
        # 3. Calcul du spread et du Z-Score GLISSANT (Fenêtre de 20 comme le backtest)
        df_chart["Spread"] = df_chart["GOOG"] - (BETA * df_chart["GOOGL"])
        
        rolling_mean = df_chart["Spread"].rolling(window=20).mean()
        rolling_std = df_chart["Spread"].rolling(window=20).std()
        df_chart["Z-Score"] = (df_chart["Spread"] - rolling_mean) / rolling_std

        # 4. Extraction du tout dernier point pour les KPIs du haut
        prix_goog = df_chart["GOOG"].iloc[-1]
        prix_googl = df_chart["GOOGL"].iloc[-1]
        z_score_actuel = df_chart["Z-Score"].iloc[-1]

        # Affichage des KPIs
        c1, c2, c3 = st.columns(3)
        c1.metric(label="Dernier prix GOOG", value=f"{prix_goog:.2f} $")
        c2.metric(label="Dernier prix GOOGL", value=f"{prix_googl:.2f} $")
        
        # Sécurité : Si on n'a pas encore 20 points, le Z-Score glissant sera NaN
        if pd.isna(z_score_actuel):
            c3.metric(label="Z-Score actuel", value="Calcul en cours...", delta="Attente de 20 points")
        else:
            c3.metric(label="Z-Score actuel", value=f"{z_score_actuel:.2f}")
        
        # 5. Conversion cosmétique des dates UTC en heure locale Paris pour le graphique
        df_chart["date"] = pd.to_datetime(df_chart["date"], format='mixed')
        df_chart["date"] = df_chart["date"].dt.tz_localize('UTC', ambiguous='NaT', nonexistent='NaT').dt.tz_convert('Europe/Paris')
        
        # Graphique du spread
        st.subheader("Graphique du spread (100 derniers points)")
        st.line_chart(df_chart.set_index("date")["Spread"])
        
        # Journal des ordres avec ajustement des dates
        st.subheader("Journal des positions émises")
        if all_orders:
            df_orders = pd.DataFrame(all_orders, columns=[
                "ID", "Date Entrée", "Date Sortie", "Signal", 
                "Statut", "Entry GOOG", "Entry GOOGL", "Exit GOOG", 
                "Exit GOOGL", "Beta", "PnL"
            ])
            
            for col in ["Date Entrée", "Date Sortie"]:
                df_orders[col] = pd.to_datetime(df_orders[col], format='mixed')
                if df_orders[col].notna().any():
                    df_orders[col] = df_orders[col].dt.tz_localize('UTC', ambiguous='NaT', nonexistent='NaT').dt.tz_convert('Europe/Paris')
            
            st.dataframe(df_orders, use_container_width=True)
        else:
            st.info("Aucun trade enregistré pour le moment.")
            
    else:
        st.warning("En attente de réception des premières données du live_feeder...")

# --- LE MOTEUR DE RAFRAÎCHISSEMENT GLOBAL ---
time.sleep(10)
st.rerun()