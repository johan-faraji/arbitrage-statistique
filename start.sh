#!/bin/bash

# 1. Lancer le live feeder en tâche de fond (il gère le reset automatique de la table orders)
echo "Démarrage du Live Feeder (Finnhub)..."
python live_feeder.py &

# Petit temps de pause pour laisser le temps au feeder de générer la base si besoin
sleep 2

# 2. Lancer le moniteur de trading en tâche de fond
echo "Démarrage du Moniteur de surveillance du Z-Score..."
python monitor_statarb.py &

# 3. Lancer le Dashboard Streamlit au premier plan
echo "Lancement du Dashboard Quant..."
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
