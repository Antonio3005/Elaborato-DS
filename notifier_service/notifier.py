from kafka import KafkaConsumer
import json
import schedule
import time
import smtplib
from email.mime.text import MIMEText

# Configurazione di Kafka
kafka_bootstrap_servers = 'your_kafka_bootstrap_servers'
kafka_topic = 'your_kafka_topic'
consumer = KafkaConsumer(kafka_topic, bootstrap_servers=kafka_bootstrap_servers,
                         value_deserializer=lambda x: json.loads(x.decode('utf-8')))

# Configurazione del database MySQL con SQLAlchemy
# ...

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
# Configurazione per l'invio dell'email
# Configurazione per l'invio dell'email
smtp_server = 'your_smtp_server'
smtp_port = 587
smtp_username = 'your_smtp_username'
smtp_password = 'your_smtp_password'
from_email = 'your_from_email'

msg = MIMEText(body)
msg['Subject'] = subject
msg['From'] = from_email
msg['To'] = to_email

with smtplib.SMTP(smtp_server, smtp_port) as server:
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(from_email, [to_email], msg.as_string())


def process_flight_data(flight_data):
    save_to_database(flight_data)

    to_email = 'recipient@example.com'  # Specifica l'indirizzo email del destinatario
    subject = 'Nuove offerte di volo disponibili!'
    body = f"Ci sono nuove offerte di volo disponibili. Controlla il nostro sito per maggiori dettagli."

    send_notification_email(to_email, subject, body)
def consume_messages():
    for message in consumer:
        flight_data = message.value
        process_flight_data(flight_data)

def trigger_api_and_consume_messages():
    response = requests.get('http://localhost:5002/')  # Chiamata all'API Service per ottenere dati aggiornati
    if response.status_code == 200:
        consume_messages()

# Scheduler per eseguire trigger_api_and_consume_messages ogni giorno alle 8:00 AM
schedule.every().day.at("08:00").do(trigger_api_and_consume_messages)

if __name__ == '__main__':
    while True:
        schedule.run_pending()
        time.sleep(1)
