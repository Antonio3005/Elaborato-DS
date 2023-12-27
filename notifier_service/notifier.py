from confluent_kafka import Consumer, KafkaError
import json
import schedule
import time
import requests
import logging
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
mail = Mail(app)

#modificare le funzioni del producer e del consumer

# Configurazione del database MySQL con SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql://an:12345@mysql_bestflights/bestflights"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurazione di Kafka
kafka_bootstrap_servers = 'kafka:9092'
kafka_topic = 'flights'
group_id = 'group'
conf = {
    'bootstrap.servers': kafka_bootstrap_servers,
    'group.id': group_id,
    'auto.offset.reset': 'earliest',  # Puoi regolare questa impostazione in base alle tue esigenze
}



# Configurazione Flask-Mail
app.config['MAIL_SERVER'] = 'an_server'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'an'
app.config['MAIL_PASSWORD'] = '12345'
app.config['MAIL_DEFAULT_SENDER'] = 'antonioinv12@gmail.com'

mail.init_app(app)

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


with app.app_context():
    db.create_all()

def save_to_database(flight_data):

    new_flight = BestFlights(
        user_id=flight_data['user_id'],
        city_from=flight_data['city_from'],
        airport_from=flight_data['airport_from'],
        airport_to=flight_data['airport_to'],
        city_to=flight_data['city_to'],
        departure_date=flight_data['departure_date'],
        return_date=flight_data['return_date'],
        price=flight_data['price']
    )
    db.session.add(new_flight)
    db.session.commit()

def send_notification_email(to_email, subject, body):
    try:
        msg = Message(subject = subject,
                      recipients=[to_email])
        msg.body = body
        mail.send(msg)
        return 'Email inviata con successo!'
    except Exception as e:
        return 'Errore durante l\'invio dell\'email: ' + str(e)



def process_flight_data(flight_data):

    save_to_database(flight_data)

    to_email =flight_data['user_id']  # Specifica l'indirizzo email del destinatario
    subject = 'Nuove offerte di volo disponibili!'
    body = f"Ci sono nuove offerte di volo disponibili per le tue richieste: {flight_data}" #da modificare
    send_notification_email(to_email, subject, body)
def consume_messages():
    from confluent_kafka import KafkaError

def consume_messages(c):
    try:
        while True:
            # Consuma i messaggi
            msg = c.poll(0.1)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break

            # Elabora il messaggio
            flight_data = msg.value()
            data = json.loads(flight_data)
            logging.debug(f"data : {data}")
            process_flight_data(data)

    except Exception as e:
        print(f"Errore durante la lettura dei messaggi: {e}")
    finally:
        # Chiudi il consumatore alla fine
        c.close()


#def trigger_api_and_consume_messages():
#    response = requests.get('http://localhost:5002/')  # Chiamata all'API Service per ottenere dati aggiornati
#    if response.status_code == 200:
#        consume_messages()

# Scheduler per eseguire trigger_api_and_consume_messages ogni giorno alle 8:00 AM

@app.route('/', methods=['GET'])
def best_flights():
    consumer = Consumer(**conf)
    consumer.subscribe([kafka_topic])

    try:
        consume_messages(consumer)
    except Exception as e:
        print(f"Errore durante la lettura dei messaggi: {e}")
    finally:
        # Chiudi il consumatore alla fine
        consumer.close()

    return "Successo"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5003)
#    while True:
#        schedule.run_pending()
#        time.sleep(1)
