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

@app.route('/weather', methods=['GET'])
def get_weather():

    subscription = UserPreferences.query.all()
    print(subscription)

    """"
    
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

    url = 'https://api.tequila.kiwi.com/v2/search'
    headers = {
        'accept': 'application/json',
        'apikey': 'D-ljrLyhPOeM1-eWQWcVliV9mBNListf'
    }

    params = {
        'fly_from': 'FRA',
        'fly_to': 'PRG',
        'date_from': '01/04/2024',
        'date_to': '03/04/2024',
        'return_from': '04/04/2024',
        'return_to': '06/04/2024',
        'nights_in_dst_from': 2,
        'nights_in_dst_to': 3,
        'max_fly_duration': 20,
        'ret_from_diff_city': True,
        'ret_to_diff_city': True,
        'one_for_city': 0,
        'one_per_date': 0,
        'adults': 2,
        'children': 2,
        'selected_cabins': 'C',
        'mix_with_cabins': 'M',
        'adult_hold_bag': '1,0',
        'adult_hand_bag': '1,1',
        'child_hold_bag': '2,1',
        'child_hand_bag': '1,1',
        'only_working_days': False,
        'only_weekends': False,
        'partner_market': 'us',
        'max_stopovers': 2,
        'max_sector_stopovers': 2,
        'vehicle_type': 'aircraft',
        'limit': 100
    }
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
