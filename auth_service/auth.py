#from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests
import logging
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__, template_folder='templates')
metrics = PrometheusMetrics(app)
CORS(app)

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

            logging.error(f"Data: {username},,{password}")


        #metrics.counter('login_attempts_total', 'Numero totale di tentativi di login').inc()
            user = User.query.filter_by(username=username, password=password).first()

            if user:
                #metrics.counter('successful_logins_total', 'Numero totale di login riusciti').inc()
                return jsonify({"success": True, "message": "Login riuscito", "username": username})
            else:
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
                #metrics.counter('registration_attempts_email_exists_total', 'Numero totale di tentativi di registrazione con email già presente').inc()
                return jsonify({"success": False, "message": "Questo username è già stato utilizzato. Scegli un altro."})

            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()

            #metrics.counter('successful_registrations_total', 'Numero totale di registrazioni riuscite').inc()
            return jsonify({"success": True, "message": "Registrazione riuscita", "username": username})
    except Exception as e:
        logging.error(f"Errore durante la registrazione: {e}")
        return jsonify({"success": False, "message": "Si è verificato un errore durante la registrazione. Riprova più tardi."})


if __name__ == '__main__':
    app.run()
