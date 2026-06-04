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

    def run(self, series1, series2):
        """
        La méthode maîtresse qui orchestre le calcul, simule les gains/pertes
        et affiche le rendement final du portefeuille.
        """
        z_score = self.calculate_zscore(series1, series2)
        signals = self.generate_signals(z_score)
        daily_returns1 = series1.pct_change()
        daily_returns2 = series2.pct_change()
        global_returns = signals.shift(1) * (daily_returns1 - daily_returns2)
        
        # 4. Évolution du capital dans le temps
        equity_curve = (1 + global_returns.fillna(0)).cumprod() * self.initial_capital
        
        # 5. Calcul des métriques de fin
        final_capital = equity_curve.iloc[-1]
        total_return = ((final_capital - self.initial_capital) / self.initial_capital) * 100
        
        print(f"Capital Initial : {self.initial_capital:,.2f} $")
        print(f"Capital Final : {final_capital:,.2f} $")
        print(f"Rendement Total : {total_return:.2f} %")
        
        return equity_curve

