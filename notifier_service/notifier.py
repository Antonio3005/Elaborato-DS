from confluent_kafka import Consumer, KafkaError
import json
import schedule
import time
import requests
import logging
from flask import Flask, render_template, request, redirect, url_for, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import grpc
import flight_pb2
import flight_pb2_grpc
from concurrent import futures
import smtplib,os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import psutil
import shutil
from prometheus_flask_exporter import PrometheusMetrics
from prometheus_client import Counter, Gauge, start_http_server
from dotenv import load_dotenv

# Carica le variabili di ambiente da .env nella directory principale
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)
load_dotenv()
# Recupera l'API key
mail_username = os.environ['MAIL_USERNAME']
mail_password = os.environ['MAIL_PASSWORD']

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
mail = Mail(app)

#modificare le funzioni del producer e del consumer

db_user = os.environ.get('MYSQL_USER')
db_password = os.environ.get('MYSQL_PASSWORD')
db_name = os.environ.get('MYSQL_DATABASE')
db_serv_name = os.environ.get('MYSQL_SERV_NAME')

# Configurazione del database MySQL con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://{db_user}:{db_password}@{db_serv_name}/{db_name}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

memory_usage = Gauge(
    'memory_usage_percent_notifier', 'Percentuale Memory usage')

cpu_usage = Gauge(
    'cpu_usage_percent_notifier', 'Percentuale CPU usage')

disk_space_usage = Gauge(
    'disk_space_usage_notifier', 'Disk space usage in bytes')

email_send_time = Gauge(
    'email_send_time_seconds', 'Tempo di invio di una email')

db = SQLAlchemy(app)

# Configurazione di Kafka
kafka_bootstrap_servers = 'kafka:9092'
kafka_topic = 'flights'
group_id = 'notifier_group'
conf = {
    'bootstrap.servers': kafka_bootstrap_servers,
    'group.id': group_id,
    'auto.offset.reset': 'earliest',  # Puoi regolare questa impostazione in base alle tue esigenze
}
consumer = Consumer(**conf)
consumer.subscribe([kafka_topic])



# Configurazione Flask-Mail
#per maggiore sicurezza utilizzare le variabili
#di ambiente del docker-compose in questo modo:
#my_variable = os.environ.get('MY_VARIABLE')
#app.config['MAIL_SERVER'] = 'smtp.libero.it'
#app.config['MAIL_PORT'] = 465
#app.config['MAIL_USE_TLS'] = False
#app.config['MAIL_USE_SSL'] = True
#app.config['MAIL_USERNAME'] = 'angelo-cocuzza@libero.it'
#app.config['MAIL_PASSWORD'] = 'Bestflights123!'
#app.config['MAIL_DEFAULT_SENDER'] = 'angelo-cocuzza@libero.it'

#mail.init_app(app)
class BestFlights(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(255), nullable=False)
    d_city_from = db.Column(db.String(255), nullable=False)
    d_airport_from = db.Column(db.String(255), nullable=False)
    d_airport_to = db.Column(db.String(255), nullable=False)
    d_city_to = db.Column(db.String(255), nullable=False)
    r_city_from = db.Column(db.String(255), nullable=False)
    r_airport_from = db.Column(db.String(255), nullable=False)
    r_airport_to = db.Column(db.String(255), nullable=False)
    r_city_to = db.Column(db.String(255), nullable=False)
    departure_date = db.Column(db.String(255), nullable=False)
    return_date = db.Column(db.String(255), nullable=False)
    price = db.Column(db.String(255), nullable=False)


with app.app_context():
    db.create_all()

#class NotifierService(flight_pb2_grpc.FlightDataServiceServicer):
    #def SendFlightData(self, request, context):
        # Parsa il campo json_data come oggetto JSON
        #logging.info("debuggo")
        #json_data = json.loads(request.json_data)
        #logging.info("Dati ricevuti da gRPC")
        #logging.info(f"{json_data}")
        # Ora json_data è un dizionario Python
        #process_flight_data(json_data)
        # Fai qualcosa con i dati JSON

        # Restituisci una risposta se necessario
        #return flight_pb2.NotifyFlightDataSuccess(message="Dati ricevuti con successo")

def save_to_database(flight_data):
    with app.app_context():
        logging.debug(f"ciao {flight_data['route'][0]}")
        try:
            new_flight = BestFlights(
                user_id=flight_data['user_id'],
                d_city_from=flight_data['route'][0]['cityFrom'],
                d_airport_from=flight_data['route'][0]['flyFrom'],
                d_airport_to=flight_data['route'][0]['flyTo'],
                d_city_to=flight_data['route'][0]['cityTo'],
                r_city_from=flight_data['route'][1]['cityFrom'],
                r_airport_from=flight_data['route'][1]['flyFrom'],
                r_airport_to=flight_data['route'][1]['flyTo'],
                r_city_to=flight_data['route'][1]['cityTo'],
                departure_date=flight_data['route'][0]['local_departure'],
                return_date=flight_data['route'][1]['local_departure'],
                price=flight_data['price']
            )

            #logging.debug(f"ciao 2 {new_flight}")
            db.session.add(new_flight)
            db.session.commit()
            return 'Database aggiornato'
        except Exception as e:
            return f'Errore durante il salvataggio nel database: {e}'

def send_notification_email(to_email, subject, body):
    try:
        start_time = time.time()
        # Configurare i dettagli del server SMTP
        smtp_server = 'smtp.libero.it'
        smtp_port = 465
        smtp_username = mail_username
        smtp_password = mail_password

        # Creare un oggetto del messaggio
        msg = MIMEMultipart()
        msg['From'] = mail_username
        msg['To'] = to_email
        msg['Subject'] = subject

        logging.debug(f"IL BODY È : {body}")

        # Aggiungere il corpo del messaggio
        #body_unicode = body.encode('utf-8').decode('utf-8')
        body_with_crlf = body.replace('\n', '\r\n')
        msg.attach(MIMEText(body, 'plain', 'utf-8'))

        # Inizializzare la connessione SMTP
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(msg['From'], msg['To'], msg.as_string())

        end_time = time.time()
        # Calcola il tempo totale di invio dell'email
        send_time = end_time - start_time
        # Registra il tempo di invio come un valore istantaneo nel Gauge
        email_send_time.set(send_time)

        logging.debug("Email inviata con successo!")
        return 'Email inviata con successo!'
    except Exception as e:
        logging.error(f'Errore durante l\'invio dell\'email: {e}')
        return 'Errore durante l\'invio dell\'email: ' + str(e)


def process_flight_data(flight_data):
    try:
        logging.debug(f"process_flight_dats : {flight_data}")
        max_price = float(flight_data['price'])  # Converti il prezzo in un numero a virgola mobile
        with app.app_context():
                existing_bf = BestFlights.query.filter_by(
                user_id=flight_data['user_id'],
                d_city_from=flight_data['route'][0]['cityFrom'],
                d_airport_from=flight_data['route'][0]['flyFrom'],
                d_airport_to=flight_data['route'][0]['flyTo'],
                d_city_to=flight_data['route'][0]['cityTo'],
                r_city_from=flight_data['route'][1]['cityFrom'],
                r_airport_from=flight_data['route'][1]['flyFrom'],
                r_airport_to=flight_data['route'][1]['flyTo'],
                r_city_to=flight_data['route'][1]['cityTo'],
                departure_date=flight_data['route'][0]['local_departure'],
                return_date=flight_data['route'][1]['local_departure']
            ).all()

        logging.debug(f"{existing_bf}")

        if existing_bf:
            for bf in existing_bf:
                if float(bf.price) > max_price:
                    logging.debug(f"Prezzo {bf.price} maggiore o uguale a {max_price}")
                    logging.debug("Nuove offerte")
                    db.session.delete(bf)
                    save_to_database(flight_data)
                    body = (f"Ci sono nuove offerte di volo disponibili per le tue richieste: \n"
                            "Andata:\n"
                            f"Citta di partenza {flight_data['route'][0]['cityFrom']}\n"
                            f"Aeroporto di partenza {flight_data['route'][0]['flyFrom']}\n"
                            f"Aeroporto di arrivo {flight_data['route'][0]['flyTo']}\n"
                            f"Citta di arrivo {flight_data['route'][0]['cityTo']}\n"
                            f"Data di partenza {flight_data['route'][0]['local_departure']}\n"
                            "Ritorno:\n"
                            f"Citta di partenza {flight_data['route'][1]['cityFrom']}\n"
                            f"Aeroporto di partenza {flight_data['route'][1]['flyFrom']}\n"
                            f"Aeroporto di arrivo {flight_data['route'][1]['flyTo']}\n"
                            f"Citta di arrivo {flight_data['route'][1]['cityTo']}\n"
                            f"Data di ritorno {flight_data['route'][1]['local_departure']}\n"
                            f"Prezzo {flight_data['price']}\n") #da modificare
                else:
                    logging.debug("Per oggi niente offerte")
                    logging.debug(f"Volo al prezzo di {max_price}")
                    body = (f"Per oggi niente offerte") #da modificare
                    #save_to_database(flight_data)

        else:
            save_to_database(flight_data)
            body = (f"Ci sono nuove offerte di volo disponibili per le tue richieste: \n"
                    "Andata:\n"
                    f"Citta di partenza {flight_data['route'][0]['cityFrom']}\n"
                    f"Aeroporto di partenza {flight_data['route'][0]['flyFrom']}\n"
                    f"Aeroporto di arrivo {flight_data['route'][0]['flyTo']}\n"
                    f"Citta di arrivo {flight_data['route'][0]['cityTo']}\n"
                    f"Data di partenza {flight_data['route'][0]['local_departure']}\n"
                    "Ritorno:\n"
                    f"Citta di partenza {flight_data['route'][1]['cityFrom']}\n"
                    f"Aeroporto di partenza {flight_data['route'][1]['flyFrom']}\n"
                    f"Aeroporto di arrivo {flight_data['route'][1]['flyTo']}\n"
                    f"Citta di arrivo {flight_data['route'][1]['cityTo']}\n"
                    f"Data di ritorno {flight_data['route'][1]['local_departure']}\n"
                    f"Prezzo {flight_data['price']}\n") #da modificare

        # Esegui il commit delle modifiche al database
        with app.app_context():
            db.session.commit()

        to_email = flight_data['user_id']  # Specifica l'indirizzo email del destinatario non funziona quando si prende con le parentesi quadre dal json stesso problema nel database vedere come risolverlo
        subject = 'Nuove offerte di volo disponibili!'
        send_notification_email(to_email, subject, body)
    except Exception as e:
        return f'Errore durante l\'elaborazione dei dati di volo: {e}'


#def serve():
    #server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    #flight_pb2_grpc.add_FlightDataServiceServicer_to_server(NotifierService(), server)
    #server.add_insecure_port('[::]:5003')
    #logging.info("Avvio del server gRPC su porta 5003...")
    #server.start()
    #logging.info("Il server gRPC è in esecuzione.")
    #server.wait_for_termination()

def consume_messages(c):
    try:
        while True:
            # Consuma i messaggi
            #i messaggi ricevuti vengono letti lentamente, una soluzione potrebbe essere ridurre il poll?
            msg = c.poll(0.1)
            logging.error(f"{msg}")
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
            process_flight_data(data)

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

def schedule_jobs():
    while(True):
        consume_messages(consumer)
        #implementare consumer kafka
        measure_metrics()
    # Aggiungi un ritardo prima di ripetere il ciclo
        time.sleep(45)


if __name__ == '__main__':
    start_http_server(5000)
    schedule_jobs()
    #serve()
