from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import os
from dotenv import load_dotenv

# Carica le variabili di ambiente da .env
load_dotenv()

app = Flask(__name__)

# Configurazione del database MySQL con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

db = SQLAlchemy(app)

class UserPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(255), nullable=False)
    temp_max = db.Column(db.Float, nullable=False)
    temp_min = db.Column(db.Float, nullable=False)


@app.route('/choice_temp', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Ottieni i valori inseriti dall'utente
        city = request.form['city']
        temp_max = request.form['temp_max']
        temp_min = request.form['temp_min']

        # Salva i valori nel database
        user_preferences = UserPreferences(city=city, temp_max=temp_max, temp_min=temp_min)
        db.session.add(user_preferences)
        db.session.commit()

        return redirect(url_for('index'))

    # Ottieni tutte le preferenze utente dal database
    preferences = UserPreferences.query.all()

    return render_template('index.html', preferences=preferences)

if __name__ == '__main__':
    app.run(debug=True, port=5001)
