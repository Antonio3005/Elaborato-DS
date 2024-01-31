import logging
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def train_and_predict_arima(dataframe, steps):
    # Addestramento del modello ARIMA
    model = ARIMA(dataframe, order=(1, 1, 1))
    results = model.fit()

    # Predizione della probabilità futura
    forecast = results.get_forecast(steps=steps)
    conf_int=forecast.conf_int().iloc[-1]
    logging.error(f"{conf_int}")
    forecast_mean = forecast.predicted_mean.iloc[-1]

    return conf_int
