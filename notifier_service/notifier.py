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

db = SQLAlchemy(app)

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
app.config['MAIL_SERVER'] = 'smtp.libero.it'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'angelo-cocuzza@libero.it'
app.config['MAIL_PASSWORD'] = 'Bestflights123!'
app.config['MAIL_DEFAULT_SENDER'] = 'angelo-cocuzza@libero.it'

mail.init_app(app)

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

def save_to_database(flight_data):

    logging.debug(f"ciao {flight_data['route'][0]}")

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

    #logging.debug(f"process_flight_dats : {flight_data}")
    max_price = float(flight_data['price'])  # Converti il prezzo in un numero a virgola mobile
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
                        f"Città di partenza {flight_data['route'][0]['cityFrom']}\n"
                        f"Aeroporto di partenza {flight_data['route'][0]['flyFrom']}\n"
                        f"Aeroporto di arrivo {flight_data['route'][0]['flyTo']}\n"
                        f"Città di arrivo {flight_data['route'][0]['cityTo']}\n"
                        f"Data di partenza {flight_data['route'][0]['local_departure']}\n"
                        "Ritorno:\n"
                        f"Città di partenza {flight_data['route'][1]['cityFrom']}\n"
                        f"Aeroporto di partenza {flight_data['route'][1]['flyFrom']}\n"
                        f"Aeroporto di arrivo {flight_data['route'][1]['flyTo']}\n"
                        f"Città di arrivo {flight_data['route'][1]['cityTo']}\n"
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
                f"Città di partenza {flight_data['route'][0]['cityFrom']}\n"
                f"Aeroporto di partenza {flight_data['route'][0]['flyFrom']}\n"
                f"Aeroporto di arrivo {flight_data['route'][0]['flyTo']}\n"
                f"Città di arrivo {flight_data['route'][0]['cityTo']}\n"
                f"Data di partenza {flight_data['route'][0]['local_departure']}\n"
                "Ritorno:\n"
                f"Città di partenza {flight_data['route'][1]['cityFrom']}\n"
                f"Aeroporto di partenza {flight_data['route'][1]['flyFrom']}\n"
                f"Aeroporto di arrivo {flight_data['route'][1]['flyTo']}\n"
                f"Città di arrivo {flight_data['route'][1]['cityTo']}\n"
                f"Data di ritorno {flight_data['route'][1]['local_departure']}\n"
                f"Prezzo {flight_data['price']}\n") #da modificare

    # Esegui il commit delle modifiche al database
    db.session.commit()

    to_email = flight_data['user_id']  # Specifica l'indirizzo email del destinatario non funziona quando si prende con le parentesi quadre dal json stesso problema nel database vedere come risolverlo
    subject = 'Nuove offerte di volo disponibili!'

    #logging.debug(f'body: {body} , to: {to_email}')
    send_notification_email(to_email, subject, body)


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
            #logging.debug(type(flight_data))
            flight_data_string = flight_data.decode('utf-8')
            #logging.debug(type(flight_data_string))
            data = json.loads(flight_data_string)
            #logging.debug(type(data))
            #data = json.loads(flight_data.decode('utf-8'))
            #logging.debug(f"data : {data}")
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
