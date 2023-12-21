from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Chiave API di OpenWeatherMap
api_key = 'f5bea9a7cd302abdca838d809883d3eb'

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/weather', methods=['GET'])
def get_weather():
    city = request.args.get('city')

    if not city:
        return jsonify({'error': 'Specificare una città nella richiesta'}), 400

    # Costruisci l'URL per l'API di OpenWeatherMap
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}'

    # Effettua la richiesta all'API di OpenWeatherMap
    response = requests.get(url)
    data = response.json()

    # Verifica se la richiesta ha avuto successo
    if response.status_code == 200:
        weather_info = {
            'city': data['name'],
            'temperature': data['main']['temp'],
            'description': data['weather'][0]['description'],
        }
        return jsonify(weather_info)
    else:
        return jsonify({'error': 'Errore durante la richiesta API'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)
