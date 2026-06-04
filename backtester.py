import pandas as pd
import numpy as np

class Backtester:
    def __init__(self, initial_capital=10000.0):
        self.initial_capital = initial_capital

    def calculate_zscore(self, series1, series2, window=20):
        """
        Cette méthode doit calculer le spread entre les deux séries,
        puis sa moyenne et son écart-type glissants pour renvoyer le Z-Score.
        """
        spread = series1 - series2
        rolling_mean = spread.rolling(window=20).mean()
        rolling_std = spread.rolling(window=20).std()
        z_score = (spread - rolling_mean) / rolling_std
        
        return z_score

    def generate_signals(self, z_score_series):
        """
        Cette méthode appliquera les seuils (+2 / -2 / 0) sur le Z-Score
        pour générer des signaux d'achat (+1), de vente (-1) ou de sortie (0).
        """
        signals = []
        current_position = 0
        for score in z_score_series:

            # Sécurité pour ignorer les NaN du début de série
            if pd.isna(score):
                signals.append(0)
                continue

            if current_position == 0:
                if score > 2 :
                    current_position = -1
                elif score < -2 :
                    current_position = 1
            elif current_position == 1:
                if score >= 0 :
                    current_position = 0
            elif current_position == -1:
                if score <= 0 :
                    current_position = 0
            
            signals.append(current_position)
        
        return pd.Series(signals, index=z_score_series.index)
    
    def calculate_max_drawdown(self, equity_curve):
        """
        Calcule le Maximum Drawdown en pourcentage à partir de l'equity curve.
        """
        # 1. Calcule la série des sommets historiques (Peaks)
        peaks = equity_curve.cummax()
        # 2. Calcule la série des drawdowns quotidiens selon la formule
        drawdowns = (equity_curve - peaks) / peaks
        # 3. Trouve le pire drawdown (le minimum) et multiplie par 100 pour le %
        mdd = drawdowns.min() * 100

        return mdd
    
    def calculate_sharpe_ratio(self, global_returns):
        """
        Calcule le Ratio de Sharpe annualisé à partir des rendements quotidiens.
        """
        mean_return = global_returns.mean()
        std_return = global_returns.std()
        
        # Sécurité : Si l'écart-type est nul ou NaN, le Sharpe n'a pas de sens statistique
        if pd.isna(std_return) or std_return == 0:
            return 0.0
            
        # Calcul du Sharpe quotidien puis annualisation
        sharpe_ratio = (mean_return / std_return) * np.sqrt(252)
        
        return sharpe_ratio

    def run(self, series1, series2):
        """
        Orchestre le backtest et affiche les résultats.
        """
        # 1. Calcul des indicateurs et signaux
        z_score = self.calculate_zscore(series1, series2)
        signals = self.generate_signals(z_score)
        
        # 2. Calcul des rendements des actifs
        daily_returns1 = series1.pct_change()
        daily_returns2 = series2.pct_change()
        
        # 3. Rendement de la stratégie (aligné avec la position de la veille)
        global_returns = signals.shift(1) * (daily_returns1 - daily_returns2)
        
        # 4. Évolution du capital dans le temps
        equity_curve = (1 + global_returns.fillna(0)).cumprod() * self.initial_capital
        
        # --- NOUVEAU : SPRINT 5 (METRIQUES AVANCEES) ---
        final_capital = equity_curve.iloc[-1]
        total_return = ((final_capital - self.initial_capital) / self.initial_capital) * 100
        
        # Appels de tes nouvelles méthodes
        max_drawdown = self.calculate_max_drawdown(equity_curve)
        sharpe_ratio = self.calculate_sharpe_ratio(global_returns)
        
        # Affichage complet dans la console
        print(f"Capital Initial : {self.initial_capital:,.2f} $")
        print(f"Capital Final   : {final_capital:,.2f} $")
        print(f"Rendement Total : {total_return:.2f} %")
        print(f"Max Drawdown    : {max_drawdown:.2f} %")
        print(f"Ratio de Sharpe : {sharpe_ratio:.2f}")
        
        return equity_curve, z_score

