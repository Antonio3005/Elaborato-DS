import logging
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from flask_cors import CORS
from datetime import datetime
import jwt
import json
from confluent_kafka import Producer
import time,psutil,shutil
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Gauge
from flask_apscheduler import APScheduler

app = Flask(__name__)
CORS(app)
SECRET_KEY=os.environ['SECRET_KEY']

kafka_bootstrap_servers = 'kafka:9092'
kafka_topic = 'users'
conf = {
    'bootstrap.servers': kafka_bootstrap_servers,
}
producer = Producer(**conf)

db_user = os.environ.get('MYSQL_USER')
db_password = os.environ.get('MYSQL_PASSWORD')
db_name = os.environ.get('MYSQL_DATABASE')
db_serv_name = os.environ.get('MYSQL_SERV_NAME')

# Configurazione del database MySQL con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{db_user}:{db_password}@{db_serv_name}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class UserPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    city_from = db.Column(db.String(255), nullable=False)
    city_to = db.Column(db.String(255), nullable=False)
    date_from = db.Column(db.String(255), nullable=False)
    date_to = db.Column(db.String(255), nullable=False)
    return_from = db.Column(db.String(255), nullable=False)
    return_to = db.Column(db.String(255), nullable=False)
    price_from = db.Column(db.String(255), nullable=False)
    price_to = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()

metrics = PrometheusMetrics(app)

successful_subscription_metric = Counter(
    'successful_subscription_total', 'Numero totale di sottoscrizioni riuscite'
)

failed_subscription_metric = Counter(
    'failed_subscription_total', 'Numero totale di sottoscrizioni fallite'
)
subscription_processing_time_metric = Gauge(
    'subscription_processing_time_seconds', 'Tempo di elaborazione delle iscrizioni'
)

memory_usage = Gauge(
    'memory_usage_percent_subscription', 'Percentuale Memory usage')

cpu_usage = Gauge(
    'cpu_usage_percent_subscription', 'Percentuale CPU usage')

disk_space_usage = Gauge(
    'disk_space_usage_subscription', 'Disk space usage in bytes')

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

def is_valid_date(date_str):
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True
    except ValueError:
        return False

def validate_preferences(city_from, city_to, date_from, date_to, return_from, return_to, price_from, price_to):
    # Verifica che price_from e price_to non siano negativi
    if float(price_from) < 1 or float(price_to) < 1:
        raise ValueError("Il prezzo non può essere minore di 1.")

    today = datetime.now()

    # Verifica che le date siano nel formato corretto e non antecedenti a oggi
    date_from = datetime.strptime(date_from, "%d/%m/%Y")
    date_to = datetime.strptime(date_to, "%d/%m/%Y")

    if not is_valid_date(date_from.strftime("%d/%m/%Y")) or not is_valid_date(date_to.strftime("%d/%m/%Y")) or date_from < today or date_to < today:
        raise ValueError("Formato data non valido o data antecedente a oggi.")

    return_from = datetime.strptime(return_from, "%d/%m/%Y")
    return_to = datetime.strptime(return_to, "%d/%m/%Y")

    if not is_valid_date(return_from.strftime("%d/%m/%Y")) or not is_valid_date(return_to.strftime("%d/%m/%Y")) or return_from < today or return_to < today:
        raise ValueError("Formato data di ritorno non valido o data antecedente a oggi.")

    # Verifica che le date di ritorno non siano antecedenti a quelle di andata
    if return_from < date_from or return_to < date_to or date_to < date_from or return_to < return_from:
        raise ValueError("Le date di ritorno non possono essere antecedenti a quelle di andata.")

    # Verifica che city_from e city_to siano diverse
    if city_from == city_to:
        raise ValueError("La città di partenza non può essere uguale a quella di destinazione.")

    # Verifica che price_from non sia maggiore di price_to
    if float(price_from) > float(price_to):
        raise ValueError("Il prezzo minimo non può essere maggiore del prezzo massimo.")


def send_to_kafka(user_preferences):
    try:
        # Convertiamo l'oggetto user_preferences in un dizionario
        preferences_dict = {
            "user_id": user_preferences.user_id,
            "city_from": user_preferences.city_from,
            "city_to": user_preferences.city_to,
            "date_from": user_preferences.date_from,
            "date_to": user_preferences.date_to,
            "return_from": user_preferences.return_from,
            "return_to": user_preferences.return_to,
            "price_from": user_preferences.price_from,
            "price_to": user_preferences.price_to
        }
        serialized_data = json.dumps(preferences_dict).encode('utf-8')

    # Invia il messaggio al topic Kafka
        producer.produce(kafka_topic, value=serialized_data)
        producer.flush()

        logging.error(f"Messaggio inviato a Kafka: {serialized_data}")
    except Exception as e:
        logging.error(f"Errore durante l'invio del messaggio a Kafka: {e}")



@app.route('/api/subscription/<token>', methods=['POST'])
def subscription(token):
    if request.method == 'POST':
        start_time = time.time()  # Registrazione del tempo di inizio
        try:
            decoded_token = jwt.decode(token, key=SECRET_KEY, algorithms=['HS256'])
            logging.error(f"{decoded_token['username']}")
            if decoded_token["expirationTime"] > time.time():
                try:
                    city_from = request.form['city_from']
                    city_to = request.form['city_to']
                    date_from = request.form['date_from']
                    date_to = request.form['date_to']
                    return_from = request.form['return_from']
                    return_to = request.form['return_to']
                    price_from = request.form['price_from']
                    price_to = request.form['price_to']

                    try:
                        validate_preferences(city_from, city_to, date_from, date_to, return_from, return_to, price_from, price_to)
                    except ValueError as ve:
                        failed_subscription_metric.inc()
                        end_time = time.time()  # Registra il tempo di fine
                        processing_time = end_time - start_time
                        subscription_processing_time_metric.set(processing_time)
                        return f"Errore durante la registrazione: {ve}"

                    user_preferences = UserPreferences(user_id=decoded_token["username"], city_from=city_from,city_to=city_to, date_from=date_from, date_to=date_to,
                                                       return_from=return_from,
                                                       return_to=return_to,
                                                       price_from=price_from,
                                                       price_to=price_to)

                    logging.error(f"auth{user_preferences}")
                    db.session.add(user_preferences)
                    db.session.commit()

                    # Invia i valori a Kafka
                    send_to_kafka(user_preferences)
                    successful_subscription_metric.inc()
                    end_time = time.time()
                    processing_time = end_time - start_time
                    subscription_processing_time_metric.set(processing_time)

                    return jsonify({"success": True, "message": "Subscription riuscita"})
                except ValueError as ve:

                    return jsonify({"success": False, "message": "Si è verificato un errore durante il login. Riprova più tardi."})
            else:
                return jsonify({"success": False, "message": "Token scaduto"})

        except:
            return jsonify({"success": False, "message": "Token non presente, rieffettua il login"})

def measure_metrics():
    logging.error("SUBSCRIPTION_METRICS")

    memory_percent = psutil.virtual_memory().percent
    memory_usage.set(memory_percent)

    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_usage.set(cpu_percent)

    disk_space = shutil.disk_usage('/')
    disk_space_usage.set(disk_space.used)

scheduler.add_job(id='metrics_job', func=measure_metrics, trigger='interval', minutes=1)

if __name__ == '__main__':
    app.run()