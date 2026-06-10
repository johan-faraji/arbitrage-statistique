# Statistical Arbitrage Platform

Plateforme de trading algorithmique et de backtesting dédiée à l'arbitrage statistique (Mean Reversion) sur la paire de trackers Alphabet (**GOOG / GOOGL**). L'application est containerisée avec Docker et déployée de manière autonome sur Render.

---

## Performances historiques de la stratégie (2021 - 2026)

L'algorithme a été testé sur la période du **1er janvier 2021 au 1er juin 2026** sur la paire d'actifs jumeaux **GOOG / GOOGL** (Alphabet).

* **Capital Initial :** 10 000,00 $* **Capital Final :** 11 407,44$
* **Rendement Total :** +14,07 %
* **Profil de Risque :** Faible (Stratégie décorrélée des mouvements directionnels du marché actions).

---

## Architecture des Données (SQLite)

Pour garantir une étanchéité totale entre l'analyse historique et l'exécution en temps réel, la base de données `finance_data.db` est divisée en deux tables distinctes :

* **`historical_prices` (Backtest) :** Contient 5 ans de données historiques journalières (Daily) de 2021 à 2026. Cette table est embarquée "en dur" dans le conteneur pour s'affranchir des limitations et blocages d'IP de l'API Yahoo Finance sur le Cloud.
* **`prices` (Trading Live) :** Contient le flux de prix haute fréquence (à la seconde) capté en direct par le WebSocket Finnhub dès que le marché américain (NASDAQ) est ouvert.

---

## Fonctionnalités principales

1. **Dashboard Quant (Streamlit) :**
   * **Onglet Live :** Visualisation graphique du spread en temps réel et du Z-Score glissant sur les 100 derniers points reçus.
   * **Onglet Backtest :** Simulation historique complète sur 5 ans avec calcul dynamique du capital final, du Return (%), du Maximum Drawdown et du Sharpe Ratio.
2. **Live Feeder (Finnhub) :** Ingestion continue des flux de transactions (ticks) de GOOG et GOOGL via une connexion WebSocket sécurisée.
3. **Moniteur de Surveillance du Z-Score :** Robot d'exécution asynchrone qui calcule le Z-Score glissant (fenêtre de 20 points) à chaque seconde et enregistre les signaux d'achat (`BUY_SPREAD`), de vente (`SELL_SPREAD`) ou de fermeture (`EXIT`) en base de données.

---

## Installation et Lancement en Local

### 1. Prérequis
* Python 3.11+
* Docker (optionnel, pour tester l'environnement de production)

### 2. Installation des dépendances
```bash
pip install -r requirements.txt
---