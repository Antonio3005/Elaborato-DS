import statsmodels.api as sm

def forecast_statsmodels(metric_name, df, start_time, end_time):
    # Creazione di un DataFrame compatibile con statsmodels
    df = df.resample('S').mean()  # Campionamento dei dati per assicurarci che siano a intervalli regolari
    df = df.fillna(df.mean())  # Gestione dei valori mancanti

    # Creazione di un modello ARIMA
    model = sm.tsa.ARIMA(df['Value'], order=(1, 1, 1))  # Esempio di modello ARIMA (p, d, q)

    # Addestramento del modello
    model_fit = model.fit(disp=0)

    # Creazione di un DataFrame futuro per le previsioni nell'intervallo specificato
    future_index = pd.date_range(start=start_time, end=end_time, freq='S')
    future_data = pd.DataFrame(index=future_index, columns=['Value'])

    # Previsione
    forecast_values = model_fit.forecast(steps=len(future_index))

    # Restituzione delle previsioni
    return {
        'metric_name': metric_name,
        'forecast_values': pd.DataFrame({'Time': future_index, 'Value': forecast_values}),
        'confidence_interval': None  # statsmodels non restituisce direttamente l'intervallo di confidenza
    }
