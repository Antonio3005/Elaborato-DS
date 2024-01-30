import time, requests, os
import logging
from flask_cors import CORS
import schedule
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import forecast
from datetime import datetime, timedelta

app = Flask(__name__)
CORS(app)

db_user = os.environ.get('MYSQL_USER')
db_password = os.environ.get('MYSQL_PASSWORD')
db_name = os.environ.get('MYSQL_DATABASE')
db_serv_name = os.environ.get('MYSQL_SERV_NAME')

# Configurazione del database MySQL con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{db_user}:{db_password}@{db_serv_name}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
PROMETHEUS = os.environ.get("PROMETHEUS")

db = SQLAlchemy(app)


class Metrics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    metric_name = db.Column(db.String(255), nullable=False)
    min_value = db.Column(db.String(255), nullable=False)
    max_value = db.Column(db.String(255), nullable=False)


with app.app_context():
    db.create_all()


@app.route("/api/add", methods=['POST'])
def add():
    try:
        if request.method == 'POST':
            metric_n = request.form['metric_name']
            min_v = request.form['min_value']
            max_v = request.form['max_value']

            new_metric = Metrics(metric_name=metric_n, min_value=min_v, max_value=max_v)
            db.session.add(new_metric)
            db.session.commit()

            return jsonify({"success": True, "message": "Metrica aggiunta"})
    except Exception as e:
        return jsonify(
            {"success": False, "message": "Si è verificato un errore durante la registrazione. Riprova più tardi."})


@app.route("/api/status", methods=['GET'])
def get_status():
    # try:
    # Recupera tutte le metriche dal database
    logging.debug("sono qui metriche")
    metrics = Metrics.query.all()
    logging.debug(f"metriche {metrics}")

    dict = {}

    for metric in metrics:
        metric_n = metric.metric_name
        min_v = float(metric.min_value)
        max_v = float(metric.max_value)

        query = metric_n

        # Esegue la query a Prometheus per ottenere il valore attuale della metrica
        response = requests.get(PROMETHEUS + '/api/v1/query', params={'query': query})
        logging.debug(f"risposta {response}")
        result = float(response.json()['data']['result'][0]['value'][1])
        logging.debug(f"risposta {result}")

        # Verifica se il valore è nel range specificato dagli SLO
        if min_v <= result <= max_v:
            dict[metric_n] = True
        else:
            dict[metric_n] = False

    return jsonify({"success": True, "message": "Stato delle metriche", "metrics": dict})


# except Exception as e:
#    logging.debug("sono qui")
#    return jsonify({"success": False, "message": "Si è verificato un errore durante l'elaborazione della richiesta."})


@app.route("/api/singlestatus/", methods=['POST'])
def get_singlestatus():
    try:
        if request.method == 'POST':
            metric_n = request.form['metric_name']

            query = metric_n

            response = requests.get(PROMETHEUS + '/api/v1/query', params={'query': query})
            result = response.json()['data']['result']

            return jsonify({"success": True, "message": "Stato della metrica", "status": result})
    except Exception as e:
        return jsonify(
            {"success": False, "message": "Si è verificato un errore durante la registrazione. Riprova più tardi."})


@app.route("/api/violations", methods=['GET'])
def get_violations():
    try:

        periods = [1, 3, 6]  # Periodi in ore

        violations_data = []

        for period in periods:
            start_time = datetime.now() - timedelta(hours=period)
            end_time = datetime.now()

            metrics = Metrics.query.all()
            logging.debug(f"{metrics}")

            violations_count = {}

            for metric in metrics:
                metric_n = metric.metric_name
                min_v = float(metric.min_value)
                max_v = float(metric.max_value)

                query = metric_n

                response = requests.get(PROMETHEUS + '/api/v1/query_range',
                                        params={'query': query, 'start': start_time.timestamp(),
                                                'end': end_time.timestamp(), 'step': '15s'})

                result = response.json()['data']['result'][0]['values']

                df = pd.DataFrame(result, columns=['Time', 'Value'])
                df['Time'] = pd.to_datetime(df['Time'], unit='s')
                df = df.set_index('Time')

                violations = 0

                for _, row in df.iterrows():
                    val = row[df.columns[0]]
                    val = float(val)
                    if val < min_v or val > max_v:
                        violations += 1

                violations_count[metric_n] = violations

            violations_data.append({f"{period}_hours": violations_count})

        return jsonify({"success": True, "message": "Violazioni generate", "violations": violations_data})

    except Exception as e:
        return jsonify(
            {"success": False, "message": "Si è verificato un errore durante l'elaborazione della richiesta."})


@app.route("/api/probability", methods=['POST'])
def get_probability():
    # try:
    # Durata in secondi della previsione nel futuro

    seconds = 21600  # 6 ore

    future_seconds = int(request.form['x_seconds'])

    metrics = Metrics.query.all()

    logging.error(f"{metrics}")

    # Dizionario con nome metrica e probabilità di violazione
    probability_data = {}

    for metric in metrics:
        metric_n = metric.metric_name
        min_v = float(metric.min_value)
        max_v = float(metric.max_value)

        query = metric_n

        response = requests.get(PROMETHEUS + '/api/v1/query_range',
                                params={'query': query, 'start': time.time() - seconds, 'end': time.time(),
                                        'step': '15s'})

        result = response.json()['data']['result'][0]['values']

        logging.debug(f"{result}")

        df = pd.DataFrame(result, columns=['Time', 'Value'])
        df['Time'] = pd.to_datetime(df['Time'], unit='s')
        df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
        df = df.set_index('Time')

        logging.debug(f"dataframe: {df}")

        # Utilizzare la tua funzione di previsione
        forecast_result = forecast.forecast(metric_n, df, df.index[-1] + pd.Timedelta(seconds=future_seconds))
        logging.debug(f"{forecast_result}")
        # Calcolare la probabilità di violazione

        """umax = conf_int['upper Value'].max()
            lmax = conf_int['lower Value'].max()
            umin = conf_int['upper Value'].min()
            lmin = conf_int['lower Value'].min()
            distanzasup = umax - lmax
            distanzainf = umin - lmin
            psup = 0
            if umax > max_v:
                psup += (umax - max_v) / distanzasup
            if lmax < min_v:
                psup += (min_v - lmax) / distanzasup
            pinf = 0
            if umin > max_v:
                psup += (umin - max_v) / distanzainf
            if lmin < min_v:
                psup += (min_v - lmin) / distanzainf
    
            probability_data[metric_n] = min(max(psup, pinf), 1)"""

    return jsonify({"success": True, "message": "Probabilità di violazione.", "probability": probability_data})


# except Exception as e:
#    return jsonify({"success": False, "message": "Si è verificato un errore durante l'elaborazione della richiesta."})


if __name__ == '__main__':
    app.run()
