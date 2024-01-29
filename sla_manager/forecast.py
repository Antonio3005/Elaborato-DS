import logging

import pandas as pd
import numpy as np
import statsmodels.api as sm

class Forecast:
    @staticmethod
    def forecast(metric_name, df, future_steps):
        """
        Prevede future violazioni di metriche utilizzando ARIMA.

        Parameters:
            metric_name (str): Nome della metrica.
            df (pd.DataFrame): DataFrame contenente la serie temporale della metrica.
            future_steps (int): Numero di passi futuri da prevedere.

        Returns:
            dict: Dizionario contenente i risultati della previsione.
        """

        # Preprocessing dei dati
        df = df.resample('S').mean()  # Campionamento dei dati per assicurarsi che siano a intervalli regolari
        df = df.fillna(df.mean())  # Gestione dei valori mancanti

        # Addestramento del modello ARIMA
        model = sm.tsa.ARIMA(df['Value'], order=(1, 1, 1))  # Esempio di modello ARIMA (p, d, q)
        result = model.fit()

        # Previsione futura
        forecast_values = result.get_forecast(steps=future_steps)

        # Estrazione degli intervalli di confidenza
        conf_int = forecast_values.conf_int()


        # Restituzione dei risultati
        return {
            'metric_name': metric_name,
            'forecast_values': forecast_values.predicted_mean.values,
            'confidence_interval': conf_int.values
        }
