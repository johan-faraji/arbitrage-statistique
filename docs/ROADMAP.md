# Roadmap des Évolutions Futures & Améliorations Techniques

Ce document détaille les axes d'amélioration identifiés pour faire évoluer la plateforme d'arbitrage statistique d'un prototype fonctionnel vers un système de trading algorithmique de niveau institutionnel.

---

## 1. Gestion des Risques : Implémentation d'un Stop-Loss Dynamique

* **Contexte Actuel :** La stratégie actuelle repose sur une confiance absolue dans le principe de retour à la moyenne (Mean Reversion). Si le Z-Score s'écarte au-delà de 2.5, le robot ouvre une position et attend passivement que le spread revienne à 0.
* **Le Risque :** En cas de déconnexion fondamentale entre GOOG et GOOGL (par exemple, une restructuration d'actions, un changement drastique des droits de vote, ou une liquidité asymétrique), le spread peut diverger à l'infini, entraînant des pertes latentes massives (Drawdown) capables de vider le capital.

### Spécifications de l'amélioration :
* **Stop-Loss Fixe sur Z-Score :** Sortie automatique de position si le Z-Score atteint un seuil critique d'invalidation (ex: $|Z| \ge 4.0$).
* **Trailing Stop (Stop Suiveur) :** Dès que le spread commence à converger en notre faveur, le niveau de stop se déplace pour verrouiller une partie des gains en cas de retournement soudain.
* **Impact sur le Backtest :** Intégrer une variable `stop_loss_threshold` dans la classe `Backtester` pour simuler l'impact de ces coupures de position sur le rendement final et valider la réduction du Maximum Drawdown.

---

## 2. Réalisme des Simulations : Prise en compte des Frais de Courtage et du Slippage

* **Contexte Actuel :** Le backtest calcule les gains de manière théorique : prix de vente moins prix d'achat. Dans le monde réel, chaque transaction engendre des coûts.
* **Le Risque :** Une stratégie qui semble rentable sur le papier peut s'avérer déficitaire en réalité si elle génère beaucoup d'ordres (Overtrading) avec des gains par trade inférieurs aux frais cumulés.

### Spécifications de l'amélioration :
* **Frais de Courtage :** Intégrer un coût fixe par ordre ou un pourcentage du montant notionnel correspondant aux grilles tarifaires des courtiers.
* **Modélisation du Slippage :** Ajouter une pénalité de prix (ex: 1 à 2 ticks, soit environ 0,01 à 0,02 $ par action sur les marchés US) pour simuler le décalage entre signal et exécution.
* **Évolution de la base de données :** Ajouter une table `orders` dédiée afin de séparer les données de marché et les données d'exécution.

---

## 3. Optimisation de la Haute Fréquence : Réduction de la Latence (Migration de SQLite vers Redis)

* **Contexte Actuel :** L'architecture actuelle utilise SQLite avec écritures disque fréquentes et lectures simultanées pour calculer le Z-Score glissant.
* **Limite :** Contention d'accès et latence liée au stockage fichier.

### Spécifications de l'amélioration :
* Migration vers une base en mémoire type Redis pour le flux temps réel.
* Conservation de SQLite uniquement en stockage historique (cold storage).
* Amélioration de la réactivité globale du système de calcul en temps réel.

---

## 4. Flexibilité de la Plateforme : Abstraction Multi-Actifs (Univers de Trading Dynamique)

* **Contexte Actuel :** Code hardcodé sur la paire GOOG / GOOGL.

### Spécifications de l'amélioration :
* Interface Streamlit avec sélection dynamique de paires.
* Ajout de paires test :
  * BRK.A / BRK.B
  * PEP / KO
  * SPY / QQQ
* Refactoring des fonctions pour accepter des tickers génériques.

---

## 5. Validation Statistique et Robustesse de la Stratégie

* **Contexte Actuel :** La stratégie est calibrée et validée sur un ensemble historique unique. Une bonne performance passée ne garantit pas sa robustesse future.
* **Le Risque :** Les paramètres peuvent être sur-optimisés (Overfitting) et produire d'excellents résultats en backtest tout en échouant rapidement en conditions réelles.

### Spécifications de l'amélioration :

* **Walk-Forward Analysis :** Découper les données historiques en plusieurs périodes d'entraînement et de validation afin de mesurer la stabilité des performances dans le temps.
* **Out-of-Sample Testing :** Réserver une partie des données historiques non utilisée pendant le développement afin d'évaluer la capacité de généralisation de la stratégie.
* **Analyse de Sensibilité :** Tester différentes combinaisons de paramètres (fenêtre glissante, seuils d'entrée/sortie, stop-loss) afin d'identifier les zones de robustesse et les dépendances excessives.
* **Surveillance de la Cointégration :** Vérifier régulièrement que les actifs de la paire restent statistiquement liés grâce à des tests tels que l'Engle-Granger ou le test de Johansen.
* **Détection de Rupture Structurelle :** Mettre en place des alertes lorsqu'une modification durable de la relation entre les actifs est détectée, indiquant une possible invalidation du modèle.
* **Mesure de la Demi-Vie du Retour à la Moyenne (Half-Life) :** Calculer et suivre l'évolution de la vitesse de convergence du spread afin de détecter une dégradation progressive de l'efficacité de la stratégie.
* **Stress Tests :** Simuler des périodes de forte volatilité, de baisse de liquidité ou d'événements exceptionnels pour évaluer le comportement du système dans des conditions défavorables.

### Indicateurs de Validation :

* Taux de réussite des trades.
* Profit Factor.
* Sharpe Ratio.
* Sortino Ratio.
* Maximum Drawdown.
* Rendement annualisé.
* Temps moyen de détention des positions.
* Stabilité des performances entre les périodes d'entraînement et de validation.

### Objectif :

Garantir que la stratégie conserve des performances acceptables en dehors de l'échantillon historique utilisé pour son développement et qu'elle reste exploitable malgré les évolutions naturelles du marché.
