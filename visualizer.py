import matplotlib.pyplot as plt

class Visualizer:
    @staticmethod
    def plot_results(equity_curve, z_score_series):
        """
        Génère un graphique professionnel à deux étages pour analyser le backtest.
        """
        # On crée une figure assez large et haute (ex: 12x8 pouces)
        # sharex=True permet de synchroniser le zoom sur les dates pour les deux graphiques
        fig, axs = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        # --- PREMIER ÉTAGE : LA COURBE DU CAPITAL ---
        axs[0].plot(equity_curve, color="green", linewidth=2, label="Capital ($)")
        axs[0].set_title("Évolution du Capital (Equity Curve) - Stratégie Arbitrage", fontsize=14, fontweight='bold')
        axs[0].set_ylabel("Capital ($)", fontsize=11)
        axs[0].grid(True, linestyle="--", alpha=0.5)
        axs[0].legend(loc="upper left")
        
        # --- DEUXIÈME ÉTAGE : LE Z-SCORE ---
        axs[1].plot(z_score_series, color="purple", linewidth=1.5, label="Z-Score du Spread")
        axs[1].set_title("Indicateur de Trading : Z-Score du Spread", fontsize=12)
        axs[1].set_ylabel("Z-Score", fontsize=11)
        axs[1].set_xlabel("Date", fontsize=11)
        
        # Ajout des lignes de seuil horizontales
        axs[1].axhline(y=2.0, color="red", linestyle="--", linewidth=1.2, label="Seuil Vente (+2)")
        axs[1].axhline(y=-2.0, color="blue", linestyle="--", linewidth=1.2, label="Seuil Achat (-2)")
        axs[1].axhline(y=0.0, color="gray", linestyle="-", linewidth=0.8) # Ligne neutre à 0
        
        axs[1].grid(True, linestyle="--", alpha=0.5)
        axs[1].legend(loc="upper left")
        
        # Ajuste automatiquement les espacements pour éviter que les textes se chevauchent
        plt.tight_layout()
        
        # Affiche la fenêtre magique
        plt.show()