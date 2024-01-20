#from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests
import os
import jwt
import time
import logging
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter

app = Flask(__name__, template_folder='templates')
metrics = PrometheusMetrics(app)

registered_users_metric = Counter(
    'registered_users_total', 'Numero totale di register riusciti'
)

registration_attempts_email_exists = Counter(
    'registration_attempts_email_exists_total', 'Numero totale di tentativi di registrazione con email già presente'
)
# metriche prometheus
logged_users_metric = Counter(
    'logged_users_total', 'Numero totale di login riusciti'
)

login_attemps_metric = Counter(
    'login_attemps_total', 'Numero totale di tentativi di login'
)

login_failed_metrics = Counter(
    'login_failed_total', 'Numero totale di login falliti'
)

CORS(app)
SECRET_KEY=os.environ['SECRET_KEY']

# Configurazione del database MySQL con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://an:12345@mysql_users/users"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

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


if __name__ == '__main__':
    app.run()
