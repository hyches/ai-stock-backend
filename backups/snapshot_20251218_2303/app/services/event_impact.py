import yfinance as yf
import pandas as pd
from datetime import timedelta

def event_impact(symbol: str, event_dates: list, window: int = 5):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period='1y')
    hist['return'] = hist['Close'].pct_change()
    impacts = []
    for event_date in event_dates:
        event_date = pd.to_datetime(event_date)
        window_data = hist.loc[(hist.index >= event_date - timedelta(days=window)) & (hist.index <= event_date + timedelta(days=window))]
        mean_return = window_data['return'].mean()
        impacts.append({'event_date': event_date, 'mean_return': mean_return})
    return impacts 