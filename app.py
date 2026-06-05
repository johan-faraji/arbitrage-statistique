import streamlit as st
import sqlite3
import pandas as pd
import time

st.set_page_config(page_title="Stream Quant Dashboard", layout="wide")
st.title("Flux de prix en temps réel (SQLite Live)")

# Connexion rapide à la base pour l'affichage
con = sqlite3.connect("finance_data.db")

# Placeholders : Ce sont des boîtes vides de Streamlit qu'on va remplir dynamiquement
metric_box = st.empty()
chart_box = st.empty()

print("Lancement de la boucle de rafraîchissement Streamlit...")

# --- À TOI DE JOUER : LA BOUCLE LIVE ---
# Crée une boucle infinie qui :
# 1. Lit les 50 dernières lignes de la table 'prices' triées par date avec Pandas :
#    df = pd.read_sql_query("SELECT * FROM prices ORDER BY date DESC LIMIT 50", conn)
# 2. Renverse le DataFrame pour avoir l'ordre chronologique : df = df.iloc[::-1]
# 3. Utilise 'metric_box.metric()' pour afficher le tout dernier prix trouvé.
# 4. Utilise 'chart_box.line_chart()' pour afficher l'évolution de la colonne 'adj_close'.
# 5. Fait une pause de 1 seconde avec time.sleep(1)
while True :
    df = pd.read_sql_query("SELECT * FROM prices ORDER BY date DESC LIMIT 50", con)
    df = df.iloc[::-1]
    if not df.empty:
        # On récupère la toute dernière ligne pour la métrique
        derniere_ligne = df.iloc[-1]
        dernier_prix = derniere_ligne['adj_close']
        actif = derniere_ligne['ticker']
        
        # 2. Mise à jour de la boîte Métrique
        metric_box.metric(label=f"Dernier prix {actif}", value=f"{dernier_prix:.2f} $")
        
        # 3. Préparation des données pour le graphique (Prix indexés par la Date)
        df_chart = df.set_index('date')['adj_close']
        
        # 4. Mise à jour du Graphique
        chart_box.line_chart(df_chart)
        
    # 5. Temporisation d'une seconde
    time.sleep(1)