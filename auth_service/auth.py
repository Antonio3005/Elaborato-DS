#from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import logging
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__, template_folder='templates')
metrics = PrometheusMetrics(app)

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

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            metrics.counter('login_attempts_total', 'Numero totale di tentativi di login').inc()  # Incrementa il contatore di tentativi di login
            user = User.query.filter_by(username=username, password=password).first()

            if user:
                metrics.counter('successful_logins_total', 'Numero totale di login riusciti').inc()  # Incrementa il contatore di login riusciti
                return redirect(f'http://0.0.0.0:5001/subscription/{username}')
            else:
                metrics.counter('failed_logins_total', 'Numero totale di login falliti').inc()  # Incrementa il contatore di login falliti
                return 'Credenziali non valide. Riprova.'

        return render_template('login.html')
    except Exception as e:
        # Registra l'errore e restituisci un messaggio di errore generico
        logging.error(f"Errore durante il login: {e}")
        return 'Si è verificato un errore durante il login. Riprova più tardi.'


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']

            if not is_valid_password(password):
                return 'La password deve essere lunga almeno 8 caratteri.'

            existing_user = User.query.filter_by(username=username).first()

            if existing_user:
                metrics.counter('registration_attempts_email_exists_total', 'Numero totale di tentativi di registrazione con email già presente').inc()
                return 'Questo username è già stato utilizzato. Scegli un altro.'

            new_user = User(username=username, password=password)
            db.session.add(new_user)
            db.session.commit()

            #send_username(username)

            return redirect(f'http://0.0.0.0:5001/subscription/{username}')

        return render_template('register.html')
    except Exception as e:
    # Registra l'errore e restituisci un messaggio di errore generico
        logging.error(f"Errore durante la registrazione: {e}")
        return 'Si è verificato un errore durante la registrazione. Riprova più tardi.'


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
