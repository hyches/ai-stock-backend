import pandas as pd
import numpy as np

def detect_market_regime(prices: pd.Series, window: int = 50):
    ma = prices.rolling(window=window).mean()
    std = prices.rolling(window=window).std()
    regime = []
    for i in range(len(prices)):
        if i < window:
            regime.append('unknown')
        elif prices.iloc[i] > ma.iloc[i] and std.iloc[i] < std.mean():
            regime.append('bull')
        elif prices.iloc[i] < ma.iloc[i] and std.iloc[i] > std.mean():
            regime.append('bear')
        else:
            regime.append('sideways')
    return pd.DataFrame({'price': prices, 'regime': regime}) 