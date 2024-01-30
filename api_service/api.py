from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
import requests
import logging
import json
from confluent_kafka import Producer, Consumer, KafkaError
import schedule
import time
import grpc
import flight_pb2
import flight_pb2_grpc
import time,os
import logging
import psutil
import shutil
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Gauge, start_http_server
from dotenv import load_dotenv

# Carica le variabili di ambiente da .env nella directory principale
#dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
#load_dotenv(dotenv_path)
load_dotenv()
# Recupera l'API key
api_key = os.environ['API_KEY']


logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)

memory_usage = Gauge(
    'memory_usage_percent_api', 'Percentuale Memory usage')

cpu_usage = Gauge(
    'cpu_usage_percent_api', 'Percentuale CPU usage')

disk_space_usage = Gauge(
    'disk_space_usage_api', 'Disk space usage in bytes')

iata_response_time = Gauge(
    'iata_response_time_seconds', 'Tempo di risposta del servizio API di IATA')

flights_response_time = Gauge(
    'flights_response_time_seconds', 'Tempo di risposta del servizio API di flights')

kafka_bootstrap_servers = 'kafka:9092'
kafka_topic1 = 'flights'
kafka_topic2 = 'users'
group_id = 'api_group'
client_id = 'api_producer'
api_consumer_conf = {
    'bootstrap.servers': kafka_bootstrap_servers,
    'group.id': group_id,
    'auto.offset.reset': 'earliest',  # Puoi regolare questa impostazione in base alle tue esigenze

}
api_producer_conf = {
    'bootstrap.servers': kafka_bootstrap_servers,
    'client.id': client_id
}
producer = Producer(**api_producer_conf)
consumer = Consumer(**api_consumer_conf)
consumer.subscribe([kafka_topic2])


db_user = os.environ.get('MYSQL_USER')
db_password = os.environ.get('MYSQL_PASSWORD')
db_name = os.environ.get('MYSQL_DATABASE')
db_serv_name = os.environ.get('MYSQL_SERV_NAME')

# Configurazione del database MySQL con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{db_user}:{db_password}@{db_serv_name}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

#scheduler = BackgroundScheduler()
#scheduler.init_app(app)
#scheduler.start()

db = SQLAlchemy(app)

#class UserPreferences(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    user_id = db.Column(db.String(255), nullable=False)
#    city_from = db.Column(db.String(255), nullable=False)
#    city_to = db.Column(db.String(255), nullable=False)
#    date_from = db.Column(db.String(255), nullable=False)
#    date_to = db.Column(db.String(255), nullable=False)
#    return_from = db.Column(db.String(255), nullable=False)
#    return_to = db.Column(db.String(255), nullable=False)
#    price_from = db.Column(db.String(255), nullable=False)
#    price_to = db.Column(db.String(255), nullable=False)

class SubPreferences(db.Model):
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
    logging.debug("cartelle create con successo")


#def send_flight_data(data):
    #logging.debug(f"sono qui dentro senf_flight;{data}")
    #channel = grpc.insecure_channel('notifier_service:5003')
    #stub = flight_pb2_grpc.FlightDataServiceStub(channel)


    # Crea un oggetto FlightDataRequest con i dati appropriati
    #request = flight_pb2.FlightDataRequest(
        #json_data=data
    #)
    #logging.debug(f"jason_data{request}")

    # Chiamata remota al servizio SendFlightData
    #response = stub.SendFlightData(request)
    #logging.debug(f"Risposta dal server: {response.message}")

def get_iata(city):

    try:
        start_time = time.time()
        url = 'https://api.tequila.kiwi.com/locations/query'
        headers = {
            'accept': 'application/json',
            'apikey': api_key
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

        end_time = time.time()  # Registra il tempo di fine della chiamata API

        # Calcola il tempo totale di risposta
        response_time = end_time - start_time

        # Registra il tempo di risposta come un valore istantaneo nel Gauge
        iata_response_time.set(response_time)


        return iata
    except Exception as e:
        print(f"Errore durante l'ottenimento di IATA per la città {city}: {e}")
        return None

# Function to get flights and insert into the database
def get_flights(iata_from, iata_to, date_from, date_to, return_from, return_to, price_from, price_to):
    try:
        start_time = time.time()
        url = 'https://api.tequila.kiwi.com/v2/search'
        headers = {
            'accept': 'application/json',
            'apikey': api_key
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

        end_time = time.time()  # Registra il tempo di fine della chiamata API

        # Calcola il tempo totale di risposta
        response_time = end_time - start_time

        # Registra il tempo di risposta come un valore istantaneo nel Gauge
        flights_response_time.set(response_time)
        return data
    except Exception as e:
        print(f"Errore durante l'ottenimento dei voli: {e}")
        return None

def flights():
    try:
        #subscription = UserPreferences.query.all()
        with app.app_context():
            subscription = SubPreferences.query.all()

        for sub in subscription:
            iata_from = get_iata(sub.city_from)
            if iata_from is None:
                continue  # Passa al prossimo record in caso di errore

            logging.debug(f"Valore di iata_from: {iata_from}")

            iata_to = get_iata(sub.city_to)
            if iata_to is None:
                continue  # Passa al prossimo record in caso di errore

            logging.debug(f"Valore di iata_to: {iata_to}")

            data = get_flights(iata_from, iata_to, sub.date_from, sub.date_to, sub.return_from, sub.return_to,
                               sub.price_from, sub.price_to)

            if data is not None:
                for d in data['data']:
                    d['user_id'] = sub.user_id
                    logging.debug(f"Valore di data: {d}")
                    serialized_data = json.dumps(d).encode('utf-8')
                    #chiamata funzione gRPC
                    #send_flight_data(serialized_data)
                    producer.produce(kafka_topic1, value=serialized_data)

                producer.flush()
    except Exception as e:
        print(f"Errore durante l'esecuzione della funzione flights: {e}")

    return 'Eseguito con successo'

def save_to_database(sub_data):
    #logging.error(f"sono qui{sub_data['city_from']}")
    try:
        with app.app_context():
            sub_preferences = SubPreferences(user_id=sub_data["user_id"],
                                               city_from=sub_data["city_from"],
                                               city_to=sub_data["city_to"],
                                               date_from=sub_data["date_from"],
                                               date_to=sub_data["date_to"],
                                               return_from=sub_data["return_from"],
                                               return_to=sub_data["return_to"],
                                               price_from=sub_data["price_from"],
                                               price_to=sub_data["price_to"])
            #logging.debug(f"ciao 2 {sub_preferences.price_from}")

            try:
                db.session.add(sub_preferences)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                logging.error(f'Errore durante il commit nel database: {e}')

            return 'Database aggiornato'
    except Exception as e:
        return f'Errore durante il salvataggio nel database: {e}'


def consume_messages(c):
    try:
        while True:
            # Consuma i messaggi
            #i messaggi ricevuti vengono letti lentamente, una soluzione potrebbe essere ridurre il poll?
            msg = c.poll(0.1)
            if msg is None:
                logging.debug("non ci sono messaggi da leggere")
                break
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break

            # Elabora il messaggio
            sub_data = msg.value()
            sub_data_string = sub_data.decode('utf-8')
            data = json.loads(sub_data_string)
            logging.error(f"{data}")
            save_to_database(data)

    except Exception as e:
        print(f"Errore durante la lettura dei messaggi: {e}")
    #finally:
        # Chiudi il consumatore alla fine
    #    c.close()


def measure_metrics():
    logging.error("AUTH_METRICS")

    memory_percent = psutil.virtual_memory().percent
    memory_usage.set(memory_percent)

    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_usage.set(cpu_percent)

    disk_space = shutil.disk_usage('/')
    disk_space_usage.set(disk_space.used)

#scheduler.add_job(measure_metrics, 'interval', minutes=1)


#schedule.every().day.at("18:58").do(flights)

def schedule_jobs():
    while True:
        #schedule.run_pending()
        #flights()
        # Esegui la funzione flights ogni giorno alle 18:58



        # Esegui altre funzioni non pianificate
        consume_messages(consumer)

        current_time = time.localtime()
        logging.debug(current_time)
        #if current_time.tm_hour == 21 and current_time.tm_min ==36 :
            #logging.debug("DEGUGGO sono qui")
        flights()

        measure_metrics()
        # Aggiungi un ritardo prima di ripetere il ciclo
        time.sleep(45)
    return "succes"



if __name__ == '__main__':
    #app.run(debug=True, host='0.0.0.0', port=5002)
    #app.run()
    #while True:
    #    schedule.run_pending()
    #    time.sleep(1)
    start_http_server(5000)
    schedule_jobs()