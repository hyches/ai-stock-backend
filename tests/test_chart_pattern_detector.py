import pandas as pd
import numpy as np
from app.services.chart_pattern_detector import extract_research_features


def make_synthetic_df(days=260):
    rng = pd.date_range(end=pd.Timestamp.today(), periods=days, freq='B')
    prices = 100 + np.cumsum(np.random.randn(days))
    high = prices + np.random.rand(days) * 2
    low = prices - np.random.rand(days) * 2
    open_ = prices + np.random.randn(days) * 0.5
    close = prices
    volume = np.random.randint(100000, 1000000, size=days)
    df = pd.DataFrame({'Open': open_, 'High': high, 'Low': low, 'Close': close, 'Volume': volume}, index=rng)
    return df


def test_extract_research_features_basic():
    df = make_synthetic_df(260)
    res = extract_research_features(df)
    assert isinstance(res, dict)
    assert 'patterns' in res
    assert 'technical_features' in res
    assert isinstance(res['pattern_count'], int)
    # technical features should include rsi_14
    assert 'rsi_14' in res['technical_features']
