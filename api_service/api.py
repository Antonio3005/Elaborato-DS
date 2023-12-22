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
class UserPreferences(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(255), nullable=False)
    temp_max = db.Column(db.String(255), nullable=False)
    temp_min = db.Column(db.String(255), nullable=False)
    rain_amount = db.Column(db.String(255), nullable=False)
    snow_presence = db.Column(db.String(255), nullable=False)

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

    import requests

    url = 'https://api.tequila.kiwi.com/v2/search'
    headers = {
        'accept': 'application/json',
        'apikey': 'qLsLVL8oCHp3riP0lbb3PTcz0TNc3r-Y'
    }

    params = {
        'fly_from': fly_from,
        'fly_to': 'PRG',
        'date_from': '01/04/2024',
        'date_to': '03/04/2024',
        'return_from': '04/04/2024',
        'return_to': '06/04/2024',
        'adults': 1,
        'adult_hand_bag': 1,
        'partner_market': 'it',
        'price_from': 10,
        'price_to': 5000,
        'vehicle_type': 'aircraft',
        'sort': 'price',
        'limit': 50
    }

    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        print(data)
    else:
        print(f"Error: {response.status_code}, {response.text}")

        flights = requests.get(url, params=params, headers=headers)

        if flights.status_code == 200:
            data = response.json()
            print(data)
        else:
        print(f"Error: {flights.status_code}, {flights.text}")

    #if not city:
    #    return jsonify({'error': 'Specificare una città nella richiesta'}), 400

    # Costruisci l'URL per l'API di OpenWeatherMap
    #url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'

    # Effettua la richiesta all'API di OpenWeatherMap
    #response = requests.get(url)
    #data = response.json()

    # Verifica se la richiesta ha avuto successo
    #if response.status_code == 200:
    #    weather_info = {
    #        'city': data['name'],
    #        'temperature': data['main']['temp'],
    #        'description': data['weather'][0]['description'],
    #    }
    #    return jsonify(weather_info)
    #else:
    #    return jsonify({'error': 'Errore durante la richiesta API'}), 500
    """

if __name__ == '__main__':
    app.run(debug=True, port=5002)
