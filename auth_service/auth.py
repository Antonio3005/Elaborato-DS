#from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests
import os
import jwt
import time
import logging
import psutil
import shutil
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Gauge
from flask_apscheduler import APScheduler

app = Flask(__name__, template_folder='templates')
metrics = PrometheusMetrics(app)

registered_users_metric = Counter(
    'registered_users_total', 'Numero totale di register riusciti'
)

registration_attempts_email_exists = Counter(
    'registration_attempts_email_exists_total', 'Numero totale di tentativi di registrazione con email già presente'
)

logged_users_metric = Counter(
    'logged_users_total', 'Numero totale di login riusciti'
)

login_attemps_metric = Counter(
    'login_attemps_total', 'Numero totale di tentativi di login'
)

login_failed_metrics = Counter(
    'login_failed_total', 'Numero totale di login falliti'
)

memory_usage = Gauge(
    'memory_usage_percent_auth', 'Percentuale Memory usage')

cpu_usage = Gauge(
    'cpu_usage_percent_auth', 'Percentuale CPU usage')

disk_space_usage = Gauge(
    'disk_space_usage_auth', 'Disk space usage in bytes')

CORS(app)
# Recupera le variabili d'ambiente
SECRET_KEY = os.environ['SECRET_KEY']
db_user = os.environ.get('MYSQL_USER')
db_password = os.environ.get('MYSQL_PASSWORD')
db_name = os.environ.get('MYSQL_DATABASE')
db_serv_name = os.environ.get('DB_SERV_NAME')

# Configurazione del database MySQL con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{db_user}:{db_password}@{db_serv_name}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)

with app.app_context():
    db.create_all()


def is_valid_password(password):
    return len(password) >= 8


@app.route('/api/login', methods=['POST'])
def api_login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            logging.debug(f"Data: {username},{password}")
            login_attemps_metric.inc()
            #metrics.counter('login_attempts_total', 'Numero totale di tentativi di login').inc()
            user = User.query.filter_by(username=username, password=password).first()

            if user:
                logged_users_metric.inc()
                #metrics.counter('successful_logins_total', 'Numero totale di login riusciti').inc()
                token=createToken(username)
                return jsonify({"success": True, "message": "Login riuscito", "token": token})
            else:
                login_failed_metrics.inc()
                #metrics.counter('failed_logins_total', 'Numero totale di login falliti').inc()
                return jsonify({"success": False, "message": "Credenziali non valide. Riprova."})
    except Exception as e:
        logging.error(f"Errore durante il login: {e}")
        return jsonify({"success": False, "message": "Si è verificato un errore durante il login. Riprova più tardi."})


@app.route('/api/register', methods=['POST'])
def api_register():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            if not is_valid_password(password):
                return jsonify({"success": False, "message": "La password deve essere lunga almeno 8 caratteri."})

            existing_user = User.query.filter_by(username=username).first()

            if existing_user:
                registration_attempts_email_exists.inc()
                #metrics.counter('registration_attempts_email_exists_total', 'Numero totale di tentativi di registrazione con email già presente').inc()
                return jsonify({"success": False, "message": "Questo username è già stato utilizzato. Scegli un altro."})

            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()

            registered_users_metric.inc()
            #metrics.counter('successful_registrations_total', 'Numero totale di registrazioni riuscite').inc()
            token=createToken(username)
            return jsonify({"success": True, "message": "Registrazione riuscita", "token": token})
    except Exception as e:
        logging.error(f"Errore durante la registrazione: {e}")
        return jsonify({"success": False, "message": "Si è verificato un errore durante la registrazione. Riprova più tardi."})

def createToken(username):
    t_data = {"username": f"{username}", "expirationTime": time.time() + 3600*2}
    token = jwt.encode(payload=t_data, key=SECRET_KEY, algorithm="HS256")
    return token

def measure_metrics():
    logging.error("AUTH_METRICS")

    memory_percent = psutil.virtual_memory().percent
    memory_usage.set(memory_percent)

    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_usage.set(cpu_percent)

    disk_space = shutil.disk_usage('/')
    disk_space_usage.set(disk_space.used)

scheduler.add_job(id='metrics_job', func=measure_metrics, trigger='interval', minutes=1)

if __name__ == '__main__':
    app.run()
