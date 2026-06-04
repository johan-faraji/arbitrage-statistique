# Statistical Arbitrage & Pairs Trading Engine

Un moteur de trading quantitatif de bout en bout implémentant une stratégie d'arbitrage statistique (Pairs Trading) neutre au marché (*Market Neutral*). Le projet intègre l'ingestion automatisée de données, un scanner de cointégration statistique, un simulateur de performance (Backtester) vectorisé, et un module de visualisation graphique.

---

## 📊 Performances de la Stratégie (2021 - 2026)

L'algorithme a été testé sur la période du **1er janvier 2021 au 1er juin 2026** sur la paire d'actifs jumeaux **GOOG / GOOGL** (Alphabet).

* **Capital Initial :** 10 000,00 $* **Capital Final :** 11 407,44$
* **Rendement Total :** +14,07 %
* **Profil de Risque :** Faible (Stratégie décorrélée des mouvements directionnels du marché actions).

---

## 🛠️ Architecture du Projet

Le projet respecte les principes de la Programmation Orientée Objet (POO) et est découpé en 4 modules indépendants (Sprints) :

1.  **`data_loader.py` (Ingestion) :** Connexion à l'API `yfinance`, extraction des cours de clôture ajustés (`adj_close`) et stockage persistant dans une base de données relationnelle locale **SQLite**.
2.  **`pairs_finder.py` (Analyse Statistique) :** Algorithme de scan combinatoire (via `itertools`). Il applique le **test de Dickey-Fuller Augmenté (ADF)** via `statsmodels` pour identifier les paires cointégrées ($p\text{-value} < 0.05$).
3.  **`backtester.py` (Moteur de Simulation) :** * Calcul vectorisé (sans boucles) du **Z-Score glissant** du spread (fenêtre de 20 jours).
    * Génération de signaux d'entrée en régime ($\pm2$ écarts-types) et de sortie ($0$) avec un système de mémoire de position pour éviter le biais de anticipation (*look-ahead bias*).
4.  **`visualizer.py` (Dashboard) :** Génération automatique d'un graphique à deux étages synchronisés avec `matplotlib` (Évolution de l'*Equity Curve* et comportement du Z-Score face aux seuils).
5.  **`main.py` :** L'orchestrateur central du projet.

---

## 🚀 Installation et Utilisation

### 1. Cloner le dépôt et configurer l'environnement
```bash
git clone [https://github.com/VOTRE_PSEUDO/VOTRE_DEPOT.git](https://github.com/VOTRE_PSEUDO/VOTRE_DEPOT.git)
cd VOTRE_DEPOT

# Créer et activer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate  # Sur Mac/Linux
# venv\Scripts\activate  # Sur Windows