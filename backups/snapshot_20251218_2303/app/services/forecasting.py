import yfinance as yf
import pandas as pd
from prophet import Prophet
from statsmodels.tsa.arima.model import ARIMA
from datetime import datetime, timedelta

class TimeSeriesForecaster:
    def __init__(self, symbol: str, period: str = '1y'):
        self.symbol = symbol
        self.period = period
        self.data = self._fetch_data()

    def _fetch_data(self):
        ticker = yf.Ticker(self.symbol)
        hist = ticker.history(period=self.period)
        hist = hist.reset_index()
        return hist[['Date', 'Close']].rename(columns={'Date': 'ds', 'Close': 'y'})

    def forecast_prophet(self, days: int = 30):
        model = Prophet()
        model.fit(self.data)
        future = model.make_future_dataframe(periods=days)
        forecast = model.predict(future)
        return forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].tail(days)

    def forecast_arima(self, days: int = 30):
        series = self.data['y']
        model = ARIMA(series, order=(5,1,0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=days)
        last_date = self.data['ds'].iloc[-1]
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days)
        return pd.DataFrame({'ds': forecast_dates, 'yhat': forecast})

def get_forecast(symbol: str, model: str = 'prophet', days: int = 30):
    forecaster = TimeSeriesForecaster(symbol)
    if model == 'prophet':
        return forecaster.forecast_prophet(days).to_dict(orient='records')
    else:
        return forecaster.forecast_arima(days).to_dict(orient='records') 