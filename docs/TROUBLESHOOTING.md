# Guide de Résolution des Problèmes & Post-Mortem 🛠️

Ce document recense les difficultés techniques majeures rencontrées lors du développement et du déploiement de la plateforme, ainsi que les solutions durables implémentées.

---

## 1. Blocage d'IP par l'API Yahoo Finance

* **Symptôme :** Requêtes de backtest en échec systématique avec des codes d'erreur HTTP (ex: 401 ou 429) uniquement lorsque l'application est déployée sur le Cloud (Render), alors que le script fonctionne parfaitement en local sur Mac.
* **Cause racine :** Les serveurs de Yahoo Finance bloquent de manière agressive les plages d'adresses IP publiques appartenant aux fournisseurs de Cloud (Render, AWS, DigitalOcean) pour empêcher le scraping de données.
* **Solution :** Architecture *Data Bake-in*. Extraction de l'historique de 5 ans en local via un script dédié (`seed_data.py`) profitant d'une IP résidentielle propre, puis intégration de la base SQLite `finance_data.db` comme un artefact figé directement poussé dans le conteneur Docker.

---

## 2. Conflit de tables entre le Backtest et le Flux Live

* **Symptôme :** Instabilité du graphique temps réel ou corruption des métriques du dashboard Streamlit lorsque le bouton de calcul du backtest était actionné simultanément.
* **Cause racine :** Utilisation d'une table SQLite unique partagée. Les processus d'écriture haute fréquence du flux live (Finnhub WebSocket) entraient en collision avec les lectures/écritures massives de l'analyse rétrospective.
* **Solution :** Isolation stricte des structures de données en base de données :
  * Table `prices` : Réservée exclusivement aux ticks temps réel.
  * Table `historical_prices` : Réservée exclusivement aux données journalières figées sur 5 ans.

---

## 3. Structure MultiIndex Pandas corrompue avec `yfinance`

* **Symptôme :** Crash du script de seeding local avec les erreurs `KeyError: 'Adj Close'` ou `float() argument must be a string or a real number, not 'Series'`.
* **Cause racine :** Les mises à jour récentes de la bibliothèque `yfinance` retournent un DataFrame avec un index de colonnes à plusieurs niveaux (*MultiIndex*) lors du téléchargement de plusieurs tickers, ce qui casse l'indexation directe par clé de Pandas.
* **Solution :** Implémentation d'un bloc de nettoyage post-téléchargement dans `seed_data.py` pour détecter le type `pd.MultiIndex`, aplatir les colonnes via `get_level_values(-1)`, et intégrer un mécanisme de secours (*fallback*) basculant sur la colonne `Close` si `Adj Close` est absent ou indéfinie.

---

## 4. Fichier de Base de Données non déployé (Fichier Fantôme)

* **Symptôme :** L'interface Streamlit sur Render indique que le backtest est indisponible car la table `historical_prices` est introuvable ou vide, bien que le fichier ait été généré localement.
* **Cause racine :** Configuration par défaut du fichier `.gitignore` (souvent héritée de templates Python standard) qui exclut automatiquement tous les fichiers se terminant par `*.db` ou `*.sqlite`, empêchant l'envoi du fichier sur le dépôt GitHub.
* **Solution :** Retrait manuel de la règle restrictive dans le fichier `.gitignore` et exécution d'un `git add finance_data.db` forcé pour valider l'indexation de la base de données.
