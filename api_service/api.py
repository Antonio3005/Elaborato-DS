from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import logging
import json
from confluent_kafka import Producer

logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)

kafka_bootstrap_servers = 'kafka:9092'
kafka_topic = 'flights'
conf = {
    'bootstrap.servers': kafka_bootstrap_servers,
}
producer = Producer(**conf)

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


# Function to get flights and insert into the database
def get_flights(iata_from, iata_to, date_from, date_to, return_from, return_to, price_from, price_to):
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

@app.route('/', methods=['GET'])
def flights():

    subscription = UserPreferences.query.all()
    print(subscription)
    for sub in subscription:
        iata_from=get_iata(sub.city_from)
        print(iata_from)
        logging.debug("Questo è un messaggio di debug.")
        logging.debug(f"Valore di iata: {iata_from}")
        iata_to=get_iata(sub.city_to)
        print(sub.city_to)
        logging.debug(f"Valore di iata: {iata_to}")
        data=get_flights(iata_from,iata_to,sub.date_from,sub.date_to,sub.return_from,sub.return_to,sub.price_from,sub.price_to)
        #data.append
        logging.debug(f"Valore di data: {data}")
        producer.produce(kafka_topic, value=data)
        # Opzionalmente, attendi la conferma dell'avvenuta consegna
        producer.flush()
        """for flight_data in data['data']:
            new_flight = BestFlights(
                user_id=sub.user_id,  # You need to provide the user_id
                city_from=flight_data['cityFrom'],
                airport_from=flight_data['flyFrom'],
                airport_to=flight_data['flyTo'],
                city_to=flight_data['cityTo'],
                departure_date=flight_data['local_departure'],
                return_date=flight_data['local_arrival'],
                price=flight_data['price']
            )
            db.session.add(new_flight)
"""
    # Commit the changes to the database
    db.session.commit()

    return 'Eseguito con successo'



if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
