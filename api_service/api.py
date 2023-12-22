
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
#import os
from dotenv import load_dotenv

# Carica le variabili di ambiente da .env
#load_dotenv()

app = Flask(__name__)
app.template_folder = 'templates'

# Configurazione del database MySQL con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://an:12345@mysql_subscription/subscription"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
class BestFlights(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    city_from = db.Column(db.String(255), nullable=False)
    airport_from = db.Column(db.String(255), nullable=False)
    airport_to = db.Column(db.String(255), nullable=False)
    city_to = db.Column(db.String(255), nullable=False)
    departure_date = db.Column(db.String(255), nullable=False)
    return_date = db.Column(db.String(255), nullable=False)
    price = db.Column(db.String(255), nullable=False)
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

def get_iata(city):

    url = 'https://api.tequila.kiwi.com/locations/query'
    headers = {
        'accept': 'application/json',
        'apikey': 'qLsLVL8oCHp3riP0lbb3PTcz0TNc3r-Y'
    }

    params = {
        'term': city,
        'locale': 'it-IT',
        'location_types': 'city',
        'limit': 10,
        'active_only': True
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        # Analizza la risposta JSON
        try:
            data = response.json()
        # Assicurati che l'array "locations" sia presente e non vuoto
            if "locations" in data and data["locations"]:
                # Estrai il valore associato alla chiave "code"
                iata = data["locations"][0]["code"]
                print(iata)
            else:
                print("Array 'locations' vuoto o assente nella risposta dell'API.")
        except json.JSONDecodeError:
        print("Errore nella decodifica della risposta JSON.")

    else:
        # Se la richiesta non è andata a buon fine, stampa il codice di stato
        print(f"Errore nella richiesta. Codice di stato: {response.status_code}")

    return iata

@app.route('/weather', methods=['GET'])
def get_weather():

    subscription = UserPreferences.query.all()
    print(subscription)





    import requests

    url = 'https://api.tequila.kiwi.com/locations/query'
    headers = {
        'accept': 'application/json',
        'apikey': 'qLsLVL8oCHp3riP0lbb3PTcz0TNc3r-Y'
    }

    params = {
        'term': 'roma',
        'locale': 'it-IT',
        'location_types': 'city',
        'limit': 10,
        'active_only': True
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Error: {response.status_code}, {response.text}")






# Function to get flights and insert into the database
def get_and_insert_flights(iata_from, iata_to, date_from, date_to, return_from, return_to, price_from, price_to):
    url = 'https://api.tequila.kiwi.com/v2/search'
    headers = {
        'accept': 'application/json',
        'apikey': 'qLsLVL8oCHp3riP0lbb3PTcz0TNc3r-Y'
    }

    params = {
        'fly_from': iata_from,
        'fly_to': iata_to,
        'date_from': date_from,
        'date_to': date_to,
        'return_from': return_from,
        'return_to': return_to,
        'adults': 1,
        'adult_hand_bag': 1,
        'partner_market': 'it',
        'price_from': price_from,
        'price_to': price_to,
        'vehicle_type': 'aircraft',
        'sort': 'price',
        'limit': 2
    }

    # Make the API request
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()

        # Iterate over the data and insert into the database

    else:
        print(f"Error: {response.status_code}, {response.text}")
    return data




if __name__ == '__main__':
    app.run(debug=True, port=5002)
