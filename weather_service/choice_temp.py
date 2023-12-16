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
    user_id = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    temp_max = db.Column(db.String(255), nullable=False)
    temp_min = db.Column(db.String(255), nullable=False)
    rain_amount = db.Column(db.String(255), nullable=False)
    snow_presence = db.Column(db.String(255), nullable=False)




@app.route('/choice_temp', methods=['GET', 'POST'])
def choice_temp():
    if request.method == 'POST':
        # Ottieni i valori inseriti dall'utente
        city = request.form['city']
        temp_max = request.form['temp_max']
        temp_min = request.form['temp_min']
        rain_amount = request.form['temp_min']
        snow_presence = request.form['temp_min']

        # Salva i valori nel database
        user_preferences = UserPreferences(user_id="antonio", city=city, temp_max=temp_max,
                                           temp_min=temp_min, rain_amount=rain_amount,
                                           snow_presence=snow_presence)
        db.session.add(user_preferences)
        db.session.commit()

        return redirect(url_for('choice_temp'))

    # Ottieni tutte le preferenze utente dal database
    #preferences = UserPreferences.query.all()

    return render_template('choice.html')#, preferences=preferences)

if __name__ == '__main__':
    app.run(debug=True, port=5001)